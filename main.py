import os
import openai
import tweepy
import requests
import re
from io import BytesIO

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True)


def generate_quote():
    chat_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Give me an existing quote from a developer with his name. Include 1-2 related hashtags for Twitter. Keep your copy short and sweet. Add in emoji or a touch of sass or silliness — and let the engagement be your guide. Your Tweet can contain up to 280 characters, formatted starting with the quote followed by the name and be conversational at the end."},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_messages,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    quote = response.choices[0].message['content'].strip()

    chat_messages.append(
        {"role": "user", "content": f"Describe the quote '{quote}' visually with detailed elements for generating an image WITHOUT any text on the image."})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_messages,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    detailed_description = response.choices[0].message['content'].strip()
    return quote, detailed_description


def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="url",
    )

    image_url = response.data[0]['url']
    return image_url


def upload_media(url):
    response = requests.get(url)
    image_data = BytesIO(response.content)

    media = api.media_upload("quote_image.png", file=image_data)
    return media.media_id_string


def extract_quote_from_tweet(tweet):
    match = re.search(r'"(.*?)"', tweet)
    return match.group(0) if match else ""


def get_all_previous_tweets():
    all_tweets = []
    max_id = None

    while True:
        tweets = api.user_timeline(
            screen_name="@DevWisdomDaily", count=200, tweet_mode="extended", max_id=max_id)
        if not tweets:
            break

        all_tweets.extend(tweets)
        max_id = tweets[-1].id - 1

    return [tweet.full_text for tweet in all_tweets]


def get_previous_quotes():
    previous_tweets = get_all_previous_tweets()
    return [extract_quote_from_tweet(tweet) for tweet in previous_tweets]


def generate_unique_quote(previous_quotes):
    quote = ""
    detailed_description = ""
    while True:
        quote, detailed_description = generate_quote()
        quote_text = extract_quote_from_tweet(quote)
        if quote_text not in previous_quotes and len(quote) <= 280:
            break
    return quote, detailed_description


def tweet_quote_and_image():
    previous_quotes = get_previous_quotes()
    quote, detailed_description = generate_unique_quote(previous_quotes)
    print("Generated quote:", quote)
    print("Generated detailed description:", detailed_description)

    image_url = generate_image(detailed_description)
    print("Generated image URL:", image_url)

    media_id = upload_media(image_url)
    print("Uploaded media ID:", media_id)

    tweet_text = quote
    api.update_status(status=tweet_text, media_ids=[media_id])
    print("Tweeted:", tweet_text)


def trigger_tweet(event, context):
    tweet_quote_and_image()
