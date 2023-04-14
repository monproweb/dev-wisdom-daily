import os
import openai
import tweepy
import re
from rapidfuzz import fuzz

# Retrieve API keys and access tokens
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Other constants
TWITTER_ACCOUNT = "@DevWisdomDaily"
MAX_STRING_LENGTH = 1000

# Check API keys and access tokens
if not OPENAI_API_KEY:
    raise ValueError("Please provide OpenAI API key.")

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY


def generate_quote(API, previous_quotes):
    """
    Generates a developer quote and image description using OpenAI GPT-3.5 Turbo,
    ensuring that the generated quote is not too similar to any previously tweeted quotes.
    Returns a tuple containing the generated quote formatted for a tweet, and
    a detailed description for generating an image using DALL-E 2.
    """
    previous_quotes = get_previous_quotes(API)
    previous_quotes_text = '\n'.join(previous_quotes)
    quote = ""
    quote_text = ""

    while True:
        chat_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant",
                "content": f"Here are some previous quotes:\n{previous_quotes_text}"},
            {"role": "user", "content": "Provide an existing quote from a well-known developer or tech figure, along with their name. Include a maximum of 1-2 related hashtags for Twitter. Keep your copy short and sweet. Add in emoji or a touch of sass or silliness — and let the engagement be your guide. Your Tweet can contain up to 280 characters maximum, formatted starting with the quote followed by the name and be conversational at the end."},
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

        if not is_quote_similar(quote_text, previous_quotes):
            break

    chat_messages.append(
        {"role": "user", "content": f"Describe the quote '{quote_text}' visually with very detailed elements up to 1000 characters for generating an image, making sure there is absolutely NO text on the image. The image should only contain visuals that represent the idea behind the quote. Please provide the description in a single block of text without line breaks."})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_messages,
        n=1,
        stop=None,
        temperature=0.7,
    )

    detailed_description = response.choices[0].message['content'].strip()
    return quote, detailed_description


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


def truncate_string(string, max_length):
    """
    Truncates the input string to the specified maximum length.
    Returns the truncated string.
    """
    return string if len(string) <= max_length else string[:max_length]


def extract_quote_from_tweet(tweet):
    """
    Extracts the quote text from the given tweet text.
    Returns the extracted quote.
    """
    match = re.search(r'"(.*?)"', tweet)
    return match.group(0) if match else ""


def is_quote_similar(quote, previous_quotes, similarity_threshold=90):
    """
    Checks if the given quote is similar to any of the previous quotes based on the similarity threshold.
    Returns True if the quote is similar, False otherwise.
    """
    for prev_quote in previous_quotes:
        similarity = fuzz.token_set_ratio(quote, prev_quote)
        if similarity >= similarity_threshold:
            return True
    return False


def generate_unique_quote(previous_quotes):
    """
    Generates a unique developer quote that is not in the given list of previous quotes
    or too similar to them. Returns a tuple containing the unique quote and its
    corresponding image description.
    """
    quote = ""
    detailed_description = ""
    while True:
        quote, detailed_description = generate_quote()
        quote_text = extract_quote_from_tweet(quote)
        if not is_quote_similar(quote_text, previous_quotes) and len(quote) <= 280:
            break
    return quote, detailed_description


def get_previous_quotes(API, TWITTER_ACCOUNT):
    all_tweets = tweepy.Cursor(
        API.user_timeline,
        screen_name=TWITTER_ACCOUNT,
        count=200,
        tweet_mode="extended",
    ).items()

    return [extract_quote_from_tweet(tweet.full_text) for tweet in all_tweets]
