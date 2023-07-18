import openai
import requests
import json
from io import BytesIO
from content_generator import ContentGenerator
from threads import Threads
import re
import tempfile
import os


def upload_media(url, bearer_token):
    response = requests.get(url)
    image_data = BytesIO(response.content).getvalue()

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "command": "INIT",
        "media_type": "image/jpg",
        "total_bytes": len(image_data),
    }
    init_response = requests.post(
        "https://upload.twitter.com/1.1/media/upload.json", headers=headers, data=data
    )
    media_id = init_response.json().get("media_id_string")

    headers["Content-Type"] = "multipart/form-data"
    data = {"command": "APPEND", "media_id": media_id, "segment_index": 0}
    files = {"media": image_data}
    append_response = requests.post(
        "https://upload.twitter.com/1.1/media/upload.json",
        headers=headers,
        data=data,
        files=files,
    )

    if append_response.status_code != 204:
        raise Exception(
            f"Media upload failed at APPEND stage with status code {append_response.status_code}, response {append_response.text}"
        )

    data = {"command": "FINALIZE", "media_id": media_id}
    finalize_response = requests.post(
        "https://upload.twitter.com/1.1/media/upload.json", headers=headers, data=data
    )

    if finalize_response.status_code != 200:
        raise Exception(
            f"Media upload failed at FINALIZE stage with status code {finalize_response.status_code}, response {finalize_response.text}"
        )

    return media_id


def handle_error(e):
    """
    Handle exceptions raised by the Twitter API.

    Args:
        e (Exception): The exception to handle.

    Raises:
        e: The original exception if it cannot be handled.
    """
    try:
        if e.api_codes and 89 in e.api_codes:
            print(
                "Invalid or expired token; please verify the validity of your "
                "Twitter API keys and access tokens."
            )
        elif e.status_code == 403:
            print(
                "Tweet not sent due to duplicate content or another violation "
                "of the Twitter rules."
            )
        else:
            raise e
    except AttributeError:
        if isinstance(e, json.JSONDecodeError):
            print("Failed to decode JSON response.")
        else:
            raise e


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
