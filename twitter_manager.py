import openai
import tweepy
import requests
from io import BytesIO
from content_generator import ContentGenerator
from threads import Threads
import re
import tempfile
import os


def setup_tweepy_client(config):
    client = tweepy.Client(
        consumer_key=config["TWITTER_API_KEY"],
        consumer_secret=config["TWITTER_API_SECRET"],
        access_token=config["TWITTER_ACCESS_TOKEN"],
        access_token_secret=config["TWITTER_ACCESS_TOKEN_SECRET"],
    )
    return client


def upload_media(url, client):
    response = requests.get(url)
    image_data = BytesIO(response.content)

    init_response = client.media_upload_init(
        "quote_image.png", file_type="image/png", total_bytes=len(image_data)
    )
    media_id = init_response["media_key"]

    for i, chunk in enumerate(image_data):
        client.media_upload_append(media_id=media_id, segment_index=i, media_data=chunk)

    client.media_upload_finalize(media_id)

    return media_id


def handle_error(e):
    if isinstance(e, tweepy.errors.Unauthorized):
        print(f"An error occurred while interacting with the Twitter API: {e}")
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


def tweet_quote_and_image(client, config):
    content_generator = ContentGenerator(client)

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

        media_id = upload_media(image_url, client)
        print(f"Uploaded media ID: {media_id}")

        quote_without_hashtags = re.sub(r"#\S+", "", quote)

        client.create_tweet(text=quote, media_ids=[media_id])
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
