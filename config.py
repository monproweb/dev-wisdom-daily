import os
import base64
import requests
from dotenv import load_dotenv


def get_bearer_token(api_key, api_secret_key):
    """
    Retrieve the Bearer token from Twitter's API.

    Args:
        api_key (str): The API key.
        api_secret_key (str): The API secret key.

    Returns:
        str: The Bearer token.

    Raises:
        Exception: If the request returned an error.
    """
    credentials = f"{api_key}:{api_secret_key}"
    b64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {b64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(
        "https://api.twitter.com/oauth2/token", headers=headers, data=data
    )

    if response.status_code != 200:
        raise Exception(
            f"Request returned an error: {response.status_code}, {response.text}"
        )

    bearer_token = response.json()["access_token"]
    return bearer_token


def get_config():
    """
    Retrieve the necessary configuration values from the environment variables.

    Returns:
        A dictionary containing the configuration values.
    """
    load_dotenv()

    twitter_api_key = os.getenv("TWITTER_API_KEY")
    twitter_api_secret = os.getenv("TWITTER_API_SECRET")
    twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not twitter_bearer_token:
        twitter_bearer_token = get_bearer_token(twitter_api_key, twitter_api_secret)

    config = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TWITTER_API_KEY": twitter_api_key,
        "TWITTER_API_SECRET": twitter_api_secret,
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "TWITTER_BEARER_TOKEN": twitter_bearer_token,
        "INSTAGRAM_USERNAME": os.getenv("INSTAGRAM_USERNAME"),
        "INSTAGRAM_PASSWORD": os.getenv("INSTAGRAM_PASSWORD"),
    }

    return config
