import os
import openai
import tweepy
import requests
import re
from io import BytesIO

# Retrieve API keys and access tokens
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check API keys and access tokens
if not TWITTER_API_KEY or not TWITTER_API_SECRET or not TWITTER_ACCESS_TOKEN or not TWITTER_ACCESS_TOKEN_SECRET:
    raise ValueError("Please provide Twitter API keys and access tokens.")
if not OPENAI_API_KEY:
    raise ValueError("Please provide OpenAI API key.")

# Other constants
TWITTER_ACCOUNT = "@DevWisdomDaily"
MAX_STRING_LENGTH = 1000

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY


def setup_tweepy_api():
    """
    Sets up and returns the Tweepy API object using the provided API keys and access tokens.
    """
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True)


def generate_quote():
    """
    Generates a developer quote and image description using OpenAI GPT-3.5 Turbo.
    Returns a tuple containing the generated quote formatted for a tweet, and
    a detailed description for generating an image using DALL-E 2.
    """
    chat_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Provide an existing quote from a well-known developer or tech figure, along with their name. Include 1-2 related hashtags for Twitter. Keep your copy short and sweet. Add in emoji or a touch of sass or silliness — and let the engagement be your guide. Your Tweet can contain up to 280 characters, formatted starting with the quote followed by the name and be conversational at the end."},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_messages,
        n=1,
        stop=None,
        temperature=0.7,
    )

    quote = response.choices[0].message['content'].strip()
    quote_text = extract_quote_from_tweet(quote)

    chat_messages.append(
        {"role": "user", "content": f"Describe the quote '{quote_text}' visually with very detailed elements up to 1000 characters for generating an image, making sure there is absolutely NO text on the image. The image should only contain visuals that represent the idea behind the quote."})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_messages,
        n=1,
        stop=None,
        temperature=0.7,
    )

    detailed_description = response.choices[0].message['content'].strip()
    return quote, detailed_description


def truncate_string(string, max_length):
    """
    Truncates the input string to the specified maximum length.
    Returns the truncated string.
    """
    return string if len(string) <= max_length else string[:max_length]


def generate_image(prompt):
    """
    Generates an image URL using OpenAI DALL-E 2 based on the given prompt.
    Returns the image URL.
    """
    truncated_prompt = truncate_string(prompt, MAX_STRING_LENGTH)
    response = openai.Image.create(
        prompt=truncated_prompt,
        n=1,
        size="1024x1024",
        response_format="url",
    )

    image_url = response.data[0]['url']
    return image_url


def upload_media(url, API):
    """
    Uploads an image to Twitter from the given URL.
    Returns the media ID string.
    """
    response = requests.get(url)
    image_data = BytesIO(response.content)

    media = API.media_upload("quote_image.png", file=image_data)
    return media.media_id_string


def extract_quote_from_tweet(tweet):
    """
    Extracts the quote text from the given tweet text.
    Returns the extracted quote.
    """
    match = re.search(r'"(.*?)"', tweet)
    return match.group(0) if match else ""


def get_previous_quotes(API):
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


def tweet_quote_and_image(API):
    """
    Generates a unique developer quote and image, and tweets them.
    """
    previous_quotes = get_previous_quotes(API)
    quote, detailed_description = generate_unique_quote(previous_quotes)
    print(f"Generated quote: {quote}")
    print(f"Generated detailed description: {detailed_description}")

    image_url = generate_image(detailed_description)
    print(f"Generated image URL: {image_url}")

    media_id = upload_media(image_url, API)
    print(f"Uploaded media ID: {media_id}")

    API.update_status(status=quote, media_ids=[media_id])
    print(f"Tweeted: {quote}")


def generate_unique_quote(previous_quotes):
    """
    Generates a unique developer quote that is not in the given list of previous quotes.
    Returns a tuple containing the unique quote and its corresponding image description.
    """
    quote = ""
    detailed_description = ""
    while True:
        quote, detailed_description = generate_quote()
        quote_text = extract_quote_from_tweet(quote)
        if quote_text not in previous_quotes and len(quote) <= 280:
            break
    return quote, detailed_description


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
