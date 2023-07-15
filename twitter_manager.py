import openai
import tweepy
import requests
from io import BytesIO
from PIL import Image
from content_generator import ContentGenerator
from threads import Threads
import re
import tempfile
import os
import json


def setup_tweepy_client(config):
    client = tweepy.Client(
        consumer_key=config["TWITTER_API_KEY"],
        consumer_secret=config["TWITTER_API_SECRET"],
        access_token=config["TWITTER_ACCESS_TOKEN"],
        access_token_secret=config["TWITTER_ACCESS_TOKEN_SECRET"],
    )
    return client


def setup_tweepy_api(config):
    auth = tweepy.OAuthHandler(config["TWITTER_API_KEY"], config["TWITTER_API_SECRET"])
    auth.set_access_token(
        config["TWITTER_ACCESS_TOKEN"], config["TWITTER_ACCESS_TOKEN_SECRET"]
    )
    return tweepy.API(auth)


def upload_media(url, API):
    response = requests.get(url)
    image_data = BytesIO(response.content)

    media = API.media_upload("quote_image.png", file=image_data)
    return media.media_id_string


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


def tweet_quote_and_image(client, API, config):
    content_generator = ContentGenerator(client)

    settings = None
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as settings_file:
            settings = json.load(settings_file)

    try:
        threads = Threads(
            username="devwisdomdaily",
            password=config["INSTAGRAM_PASSWORD"],
            settings=settings,
        )
    except Exception as e:
        print("An error occurred while setting up Threads: ", e)
        threads = None

    try:
        quote, quote_text = content_generator.generate_quote()
        print(f"Generated quote: {quote}")

        detailed_description = content_generator.generate_detailed_description(
            quote_text
        )
        print(f"Generated detailed description: {detailed_description}")

        image_url = content_generator.generate_image(detailed_description)
        print(f"Generated image URL: {image_url}")

        media_id = upload_media(image_url, API)
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

            with open("settings.json", "w") as settings_file:
                json.dump(threads.private_api.get_settings(), settings_file)

        except Exception as e:
            print("An error occurred while interacting with Threads: ", e)
    else:
        print("Threads was not set up correctly.")
