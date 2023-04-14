from twitter_utils import setup_tweepy_api, tweet_quote_and_image
from gpt_utils import get_previous_quotes


def trigger_tweet(event, context):
    """
    Trigger function to tweet a developer quote and image.
    """
    API = setup_tweepy_api()
    previous_quotes = get_previous_quotes(API)
    tweet_quote_and_image(API, previous_quotes)


def main():
    """
    The main function that triggers the tweet_quote_and_image() function.
    """
    API = setup_tweepy_api()
    previous_quotes = get_previous_quotes(API)
    tweet_quote_and_image(API, previous_quotes)


if __name__ == "__main__":
    main()
