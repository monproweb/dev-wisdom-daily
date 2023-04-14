from twitter_utils import setup_tweepy_api, tweet_quote_and_image


def trigger_tweet(event, context):
    """
    Trigger function to tweet a developer quote and image.
    """
    API = setup_tweepy_api()
    tweet_quote_and_image(API)


def main():
    """
    The main function that triggers the tweet_quote_and_image() function.
    """
    API = setup_tweepy_api()
    tweet_quote_and_image(API)


if __name__ == "__main__":
    main()
