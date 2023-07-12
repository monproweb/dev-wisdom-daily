import os
from dotenv import load_dotenv


def get_config():
    """
    Retrieve API keys and access tokens from environment variables.

    Returns:
        dict: A dictionary containing the API keys and access tokens.

    Raises:
        ValueError: If any of the API keys or access tokens is missing.
    """
    load_dotenv()

    config = {
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }

    for key, value in config.items():
        if not value:
            raise ValueError(f"Please provide {key}.")

    return config
