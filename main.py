import openai
from config import get_config
from twitter_manager import tweet_quote_and_image


def trigger_tweet(event, context):
    """
    Trigger the tweet process to generate a quote, a detailed description, and tweet them as an image.

    Args:
        event (dict): A dictionary containing data about the triggering event (not used in this function).
        context (google.cloud.functions.Context): Metadata about the function invocation (not used in this function).
    """
    config = get_config()
    openai.api_key = config["OPENAI_API_KEY"]
    bearer_token = config["TWITTER_BEARER_TOKEN"]
    tweet_quote_and_image(config, bearer_token)


def main():
    """
    The main function that triggers the tweet process. It sets up the Tweepy API,
    generates a unique quote and its corresponding image description, and tweets them as an image.
    """
    config = get_config()
    openai.api_key = config["OPENAI_API_KEY"]
    bearer_token = config["TWITTER_BEARER_TOKEN"]
    tweet_quote_and_image(config, bearer_token)


if __name__ == "__main__":
    main()
