import openai
import requests
import json
from io import BytesIO
from content_generator import ContentGenerator
from threads import Threads
import re
import tempfile
import os
import base64
from requests.structures import CaseInsensitiveDict


def upload_media(url, bearer_token):
    response = requests.get(url)
    image_data = BytesIO(response.content).getvalue()
    headers = CaseInsensitiveDict()
    headers["Authorization"] = f"Bearer {bearer_token}"
    headers["Content-Type"] = "multipart/form-data"
    base64_image = base64.b64encode(image_data).decode("utf-8")
    media_data = {"media_data": base64_image}
    media_response = requests.post(
        "https://upload.twitter.com/1.1/media/upload.json",
        headers=headers,
        data=media_data,
    )
    return media_response.json()["media_id_string"]


def handle_error(e):
    if e.api_codes and 89 in e.api_codes:
        print("Please check your Twitter API keys and access tokens.")
    elif isinstance(e, openai.error.APIError):
        print(f"OpenAI API returned an API Error: {e}")
    elif isinstance(e, openai.error.APIConnectionError):
        print(f"Failed to connect to OpenAI API: {e}")
    elif isinstance(e, openai.error.RateLimitError):
        print(f"OpenAI API request exceeded rate limit: {e}")
    else:
        print(f"An unexpected error occurred: {e}")


def tweet_quote_and_image(bearer_token, config):
    content_generator = ContentGenerator(bearer_token)

    try:
        threads = Threads(
            username="devwisdomdaily", password=config["INSTAGRAM_PASSWORD"]
        )
    except Exception as e:
        print("An error occurred while setting up Threads: ", e)
        threads = None

    try:
        previous_quotes = content_generator.get_previous_quotes()

        quote, quote_text = content_generator.generate_quote(previous_quotes)
        print(f"Generated quote: {quote}")

        detailed_description = content_generator.generate_detailed_description(
            quote_text
        )
        print(f"Generated detailed description: {detailed_description}")

        image_url = content_generator.generate_image(detailed_description)
        print(f"Generated image URL: {image_url}")

        media_id = upload_media(image_url, bearer_token)
        print(f"Uploaded media ID: {media_id}")

        quote_without_hashtags = re.sub(r"#\S+", "", quote)

        headers = {"Authorization": f"Bearer {bearer_token}"}
        data = {"status": quote, "media_ids": [media_id]}
        response = requests.post(
            "https://api.twitter.com/1.1/statuses/update.json",
            headers=headers,
            data=data,
        )
        if response.status_code != 200:
            raise Exception(
                f"Request returned an error: {response.status_code}, {response.text}"
            )
        print(f"Tweeted: {quote}")

    except Exception as e:
        handle_error(e)

    if threads:
        try:
            response = requests.get(image_url, stream=True)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                for chunk in response.iter_content(1024):
                    temp_file.write(chunk)
                temp_filename = temp_file.name

            print(f"Temp file name: {temp_filename}")

            with open(temp_filename, "rb") as image_file:
                created_thread = threads.private_api.create_thread(
                    caption=quote_without_hashtags,
                    image_file=image_file,
                )
            print(f"Posted to Threads: {created_thread}")

            os.remove(temp_filename)

        except Exception as e:
            print("An error occurred while interacting with Threads: ", e)
    else:
        print("Threads was not set up correctly.")
