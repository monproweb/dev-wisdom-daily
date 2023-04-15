import os
import openai
from openai import OpenAIError
import tweepy
import requests
import re
from io import BytesIO
from rapidfuzz import fuzz

# Retrieve API keys and access tokens
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check API keys and access tokens
if (
    not TWITTER_API_KEY
    or not TWITTER_API_SECRET
    or not TWITTER_ACCESS_TOKEN
    or not TWITTER_ACCESS_TOKEN_SECRET
):
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

    Returns:
        tweepy.API: An instance of the Tweepy API object.
    """
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True)


def extract_quote_from_tweet(tweet):
    """
    Extracts the quote text from the given tweet text.

    Args:
        tweet (str): The text of a tweet containing a quote.

    Returns:
        str: The extracted quote.
    """
    match = re.search(r'"(.*?)"', tweet)
    return match.group(0) if match else ""


def get_previous_quotes(API):
    """
    Fetches all previous quotes tweeted by the specified Twitter account.

    Args:
        API (tweepy.API): An instance of the Tweepy API object.

    Returns:
        list[str]: A list of previous quotes.
    """
    all_tweets = tweepy.Cursor(
        API.user_timeline,
        screen_name=TWITTER_ACCOUNT,
        count=200,
        tweet_mode="extended",
    ).items()

    return [extract_quote_from_tweet(tweet.full_text) for tweet in all_tweets]


def is_quote_similar(quote, previous_quotes_text, similarity_threshold=90):
    """
    Checks if the given quote is similar to any of the previous quotes based on the similarity threshold.

    Args:
        quote (str): The quote to be checked for similarity.
        previous_quotes (list[str]): A list of previous quotes to compare against.
        similarity_threshold (int, optional): The similarity threshold to be considered a match. Defaults to 90.

    Returns:
        bool: True if the quote is similar, False otherwise.
    """
    for prev_quote in previous_quotes_text.split("\n"):
        similarity = fuzz.token_set_ratio(quote, prev_quote)
        if similarity >= similarity_threshold:
            return True
    return False


def truncate_string(string, max_length):
    """
    Truncates the input string to the specified maximum length.

    Args:
        string (str): The string to be truncated.
        max_length (int): The maximum length of the truncated string.

    Returns:
        str: The truncated string.
    """
    return string if len(string) <= max_length else string[:max_length]


def generate_image(prompt):
    """
    Generates an image URL using OpenAI DALL-E 2 based on the given prompt.

    Args:
        prompt (str): The prompt to generate an image URL.

    Returns:
        str: The image URL generated by DALL-E 2.
    """
    truncated_prompt = truncate_string(prompt, MAX_STRING_LENGTH)
    response = openai.Image.create(
        prompt=truncated_prompt,
        n=1,
        size="1024x1024",
        response_format="url",
    )

    image_url = response.data[0]["url"]
    return image_url


def upload_media(url, API):
    """
    Uploads an image to Twitter from the given URL.

    Args:
        url (str): The URL of the image to be uploaded.
        API (tweepy.API): An instance of the Tweepy API object.

    Returns:
        str: The media ID string of the uploaded image.
    """
    response = requests.get(url)
    image_data = BytesIO(response.content)

    media = API.media_upload("quote_image.png", file=image_data)
    return media.media_id_string


def generate_quote(API, previous_quotes_text):
    """
    Generates a developer quote using OpenAI GPT-3.5 Turbo, ensuring that the generated quote is not too similar
    to any previously tweeted quotes.

    Args:
        API (tweepy.API): The Tweepy API object.
        previous_quotes_text (str): A string containing all previous quotes, separated by newlines.

    Returns:
        str: The generated quote formatted for a tweet.
    """
    quote = ""
    quote_text = ""

    while True:
        chat_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "assistant",
                "content": f"Here are some previous quotes:\n{previous_quotes_text}",
            },
            {
                "role": "user",
                "content": "Provide an existing quote from a well-known software developer, programmer, software engineer or tech figure, along with their name. Include a maximum of 1-2 related hashtags for Twitter. Keep your copy short and sweet. Add in emoji or a touch of sass or silliness — and let the engagement be your guide. Your Tweet can contain up to 280 characters maximum, formatted starting with the quote followed by the name and be conversational at the end.",
            },
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_messages,
            n=1,
            stop=None,
            temperature=0.7,
        )

        quote = response.choices[0].message["content"].strip()
        quote_text = extract_quote_from_tweet(quote)

        if not is_quote_similar(quote_text, previous_quotes_text) and len(quote) <= 280:
            break

    return quote, quote_text


def generate_detailed_description(quote_text, examples):
    """
    Generates a detailed description for an image using OpenAI GPT-3.5 Turbo based on the given quote_text.

    Args:
        quote_text (str): The quote text to base the image description on.
        example_text (str): A string containing examples of image descriptions, separated by newlines.

    Returns:
        str: The detailed description for generating an image using DALL-E 2.
    """
    example_text = "\n".join(examples)

    chat_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"Describe the quote '{quote_text}' visually with very detailed elements up to 1000 characters for generating an image, making sure there is absolutely NO text on the image. The image should only contain visuals that represent the idea behind the quote. Please provide the description in a single block of text without line breaks. Also, consider the following examples for inspiration: {example_text}",
        },
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_messages,
        n=1,
        stop=None,
        temperature=0.7,
    )

    detailed_description = response.choices[0].message["content"].strip()
    return detailed_description


def generate_unique_quote(previous_quotes, API):
    """
    Generates a unique developer quote that is not in the given list of previous quotes
    or too similar to them.

    Args:
        previous_quotes (list[str]): A list of previous quotes to avoid duplicates.
        API (tweepy.API): An instance of the Tweepy API object.

    Returns:
        tuple: A tuple containing the unique quote (str) and its corresponding image description (str).
    """
    quote = ""
    detailed_description = ""
    while True:
        quote, detailed_description = generate_quote(API)
        quote_text = extract_quote_from_tweet(quote)
        if not is_quote_similar(quote_text, previous_quotes) and len(quote) <= 280:
            break
    return quote, detailed_description


def tweet_quote_and_image(API):
    """
    Tweets the given quote and an image generated based on the detailed_description.

    Args:
        API (tweepy.API): The Tweepy API object.
        quote (str): The quote to be tweeted.
        detailed_description (str): The detailed description for generating an image using DALL-E 2.
    """
    try:
        previous_quotes = get_previous_quotes(API)
        previous_quotes_text = "\n".join(previous_quotes)

        quote, quote_text = generate_quote(API, previous_quotes_text)
        print(f"Generated quote: {quote}")

        examples = [
            "3D render of a cute tropical fish in an aquarium on a dark blue background, digital art",
            "An armchair in the shape of an avocado",
            "An expressive oil painting of a basketball player dunking, depicted as an explosion of a nebula",
            "A photo of a white fur monster standing in a purple room",
            "An oil painting by Matisse of a humanoid robot playing chess",
            "A photo of a silhouette of a person in a color lit desert at night",
            "A blue orange sliced in half laying on a blue floor in front of a blue wall",
            "A 3D render of an astronaut walking in a green desert",
            "A futuristic neon lit cyborg face",
            "A computer from the 90s in the style of vaporwave",
            "A cartoon of a monkey in space",
            "A plush toy robot sitting against a yellow wall",
            "A bowl of soup that is also a portal to another dimension, digital art",
            "A van Gogh style painting of an American football player",
            '"A sea otter with a pearl earring" by Johannes Vermeer',
            "A hand drawn sketch of a Porsche 911",
            "High quality photo of a monkey astronaut",
            "A cyberpunk monster in a control room",
            "A photo of Michelangelo's sculpture of David wearing headphones djing",
            "An abstract painting of artificial intelligence",
            "An Andy Warhol style painting of a french bulldog wearing sunglasses",
            "A photo of a Samoyed dog with its tongue out hugging a white Siamese cat",
            "A photo of a teddy bear on a skateboard in Times Square",
            "An abstract oil painting of a river",
            "A futuristic cyborg poster hanging in a neon lit subway station",
            "An oil pastel drawing of an annoyed cat in a spaceship",
            "A sunlit indoor lounge area with a pool with clear water and another pool with translucent pastel pink water, next to a big window, digital art",
            "A centered explosion of colorful powder on a black background",
            "A synthwave style sunset above the reflecting water of the sea, digital art",
            "A handpalm with a tree growing on top of it",
            "A cartoon of a cat catching a mouse",
            "A pencil and watercolor drawing of a bright city in the future with flying cars",
            "A Formula 1 car driving on a neon road",
            "3D render of a pink balloon dog in a violet room",
            "A photograph of a sunflower with sunglasses on in the middle of the flower in a field on a bright sunny day",
            "Two futuristic towers with a skybridge covered in lush foliage, digital art",
            "A hand-drawn sailboat circled by birds on the sea at sunrise",
            "A Shiba Inu dog wearing a beret and black turtleneck",
            "A comic book cover of a superhero wearing headphones",
            "An abstract visual of artificial intelligence",
            "A cat riding a motorcycle",
            "A 3D render of a rainbow colored hot air balloon flying above a reflective lake",
        ]

        detailed_description = generate_detailed_description(quote_text, examples)
        print(f"Generated detailed description: {detailed_description}")

        image_url = generate_image(detailed_description)
        print(f"Generated image URL: {image_url}")

        media_id = upload_media(image_url, API)
        print(f"Uploaded media ID: {media_id}")

        API.update_status(status=quote, media_ids=[media_id])
        print(f"Tweeted: {quote}")

    except tweepy.TweepyException as e:
        print(f"An error occurred while interacting with the Twitter API: {e}")
        if e.api_code == 89:  # Invalid or expired token
            print("Please check your Twitter API keys and access tokens.")
    except OpenAIError as e:
        print(f"An error occurred while interacting with the OpenAI API: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def trigger_tweet(event, context):
    """
    Triggers the tweet process to generate a quote, a detailed description, and tweet them as an image.

    Args:
        event (dict): A dictionary containing data about the triggering event (not used in this function).
        context (google.cloud.functions.Context): Metadata about the function invocation (not used in this function).
    """
    API = setup_tweepy_api()
    tweet_quote_and_image(API)


def main():
    """
    The main function that triggers the tweet_quote_and_image() function. It sets up the Tweepy API,
    generates a unique quote and its corresponding image description, and tweets them as an image.
    """
    API = setup_tweepy_api()
    tweet_quote_and_image(API)


if __name__ == "__main__":
    main()
