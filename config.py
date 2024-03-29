import os
from dotenv import load_dotenv


def get_config():
    """
    Retrieve the necessary configuration values from the environment variables.

    Returns:
        A dictionary containing the configuration values.
    """
    load_dotenv()

    config = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN"),
        "MONGODB_USERNAME": os.getenv("MONGODB_USERNAME"),
        "MONGODB_PASSWORD": os.getenv("MONGODB_PASSWORD"),
        "FACEBOOK_ACCESS_TOKEN": os.getenv("FACEBOOK_ACCESS_TOKEN"),
        "INSTAGRAM_USER_ID": os.getenv("INSTAGRAM_USER_ID"),
    }

    return config
