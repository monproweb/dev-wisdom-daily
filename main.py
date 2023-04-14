from twitter_utils import setup_tweepy_api, tweet_quote_and_image
from gpt_utils import TWITTER_ACCOUNT, get_previous_quotes, generate_quote, generate_image


def trigger_tweet(event, context):
    """
    Trigger function to tweet a developer quote and image.
    """
    API = setup_tweepy_api()
    previous_quotes = get_previous_quotes(API, TWITTER_ACCOUNT)
    quote, image_description = generate_quote(API, previous_quotes)
    image_url = generate_image(image_description)
    tweet_quote_and_image(API, quote, image_url)


def main():
    """
    The main function that triggers the tweet_quote_and_image() function.
    """
    API = setup_tweepy_api()
    previous_quotes = get_previous_quotes(API, TWITTER_ACCOUNT)
    quote, image_description = generate_quote(API, previous_quotes)
    image_url = generate_image(image_description)
    tweet_quote_and_image(API, quote, image_url)


if __name__ == "__main__":
    main()
