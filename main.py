import openai
from config import get_config
from twitter_manager import TwitterManager
from threads_manager import ThreadsManager
from content_generator import ContentGenerator


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
    twitter_manager = TwitterManager(config, bearer_token)
    threads_manager = ThreadsManager(config)
    content_generator = ContentGenerator()
    quote_without_hashtags, image_url = twitter_manager.tweet_quote_and_image(
        content_generator
    )
    threads_manager.thread_quote_and_image(quote_without_hashtags, image_url)


def main():
    """
    The main function that triggers the tweet process. It sets up the Tweepy API,
    generates a unique quote and its corresponding image description, and tweets them as an image.
    """
    config = get_config()
    openai.api_key = config["OPENAI_API_KEY"]
    bearer_token = config["TWITTER_BEARER_TOKEN"]
    twitter_manager = TwitterManager(config, bearer_token)
    threads_manager = ThreadsManager(config)
    content_generator = ContentGenerator()
    quote_without_hashtags, image_url = twitter_manager.tweet_quote_and_image(
        content_generator
    )
    threads_manager.thread_quote_and_image(quote_without_hashtags, image_url)


if __name__ == "__main__":
    main()
