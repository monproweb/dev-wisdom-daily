import os
import tweepy
import requests
from io import BytesIO
from gpt_utils import extract_quote_from_tweet

# Retrieve API keys and access tokens
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

# Other constants
TWITTER_ACCOUNT = "@DevWisdomDaily"

# Check API keys and access tokens
if not TWITTER_API_KEY or not TWITTER_API_SECRET or not TWITTER_ACCESS_TOKEN or not TWITTER_ACCESS_TOKEN_SECRET:
    raise ValueError("Please provide Twitter API keys and access tokens.")


def setup_tweepy_api():
    """
    Sets up and returns the Tweepy API object using the provided API keys and access tokens.
    """
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True)


def get_previous_quotes(API, TWITTER_ACCOUNT):
    """
    Fetches all previous quotes tweeted by the specified Twitter account.
    Returns a list of previous quotes.
    """
    all_tweets = tweepy.Cursor(
        API.user_timeline,
        screen_name=TWITTER_ACCOUNT,
        count=200,
        tweet_mode="extended",
    ).items()

    return [extract_quote_from_tweet(tweet.full_text) for tweet in all_tweets]


def upload_media(url, API):
    """
    Uploads an image to Twitter from the given URL.
    Returns the media ID string.
    """
    response = requests.get(url)
    image_data = BytesIO(response.content)

    media = API.media_upload("quote_image.png", file=image_data)
    return media.media_id_string


def tweet_quote_and_image(API, quote, image_url):
    """
    Tweets the given quote and image.
    """
    media_id = upload_media(image_url, API)

    API.update_status(status=quote, media_ids=[media_id])
