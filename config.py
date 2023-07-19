import os


def get_config():
    """
    Retrieve the necessary configuration values from the environment variables.

    Returns:
        A dictionary containing the configuration values.
    """
    config = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN"),
        "INSTAGRAM_USERNAME": os.getenv("INSTAGRAM_USERNAME"),
        "INSTAGRAM_PASSWORD": os.getenv("INSTAGRAM_PASSWORD"),
    }

    return config
