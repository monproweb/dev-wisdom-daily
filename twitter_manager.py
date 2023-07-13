import openai
import tweepy
import requests
from io import BytesIO
from content_generator import ContentGenerator


def setup_tweepy_client(config):
    """
    Set up the Tweepy Client object using the provided API keys and access tokens.

    Args:
        config (dict): A dictionary containing the API keys and access tokens.

    Returns:
        tweepy.Client: An instance of the Tweepy Client object.
    """
    client = tweepy.Client(
        consumer_key=config["TWITTER_API_KEY"],
        consumer_secret=config["TWITTER_API_SECRET"],
        access_token=config["TWITTER_ACCESS_TOKEN"],
        access_token_secret=config["TWITTER_ACCESS_TOKEN_SECRET"],
    )
    return client


def setup_tweepy_api(config):
    """
    Set up the Tweepy API object using the provided API keys and access tokens.

    Args:
        config (dict): A dictionary containing the API keys and access tokens.

    Returns:
        tweepy.API: An instance of the Tweepy API object.
    """
    auth = tweepy.OAuthHandler(config["TWITTER_API_KEY"], config["TWITTER_API_SECRET"])
    auth.set_access_token(
        config["TWITTER_ACCESS_TOKEN"], config["TWITTER_ACCESS_TOKEN_SECRET"]
    )
    return tweepy.API(auth)


def upload_media(url, API):
    """
    Upload an image to Twitter from a given URL.

    Args:
        url (str): The URL of the image to be uploaded.
        API (tweepy.API): An instance of the Tweepy API object.

    Returns:
        str: The media ID string of the uploaded image.
    """
    response = requests.get(url)
    image_data = BytesIO(response.content)

    media = API.media_upload("quote_image.png", file=image_data)
    return media.media_id_string


def handle_error(e):
    """
    Handle various errors that may occur during interaction with the Twitter and OpenAI APIs.

    This function will print an error message based on the type of error encountered, providing
    additional information for API errors and suggesting a solution for unauthorized access.

    Args:
        e (Exception): The exception raised during interaction with the APIs.
    """
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


def tweet_quote_and_image(client, API):
    """
    Generate a quote, a detailed description, an image, and tweet them.

    Args:
        client (tweepy.Client): The Tweepy Client object.
    """
    content_generator = ContentGenerator(client)

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

        client.create_tweet(text=quote, media_ids=[media_id])
        print(f"Tweeted: {quote}")
    except Exception as e:
        handle_error(e)
