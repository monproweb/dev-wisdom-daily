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

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

# Other constants
TWITTER_ACCOUNT = "@DevWisdomDaily"


def check_api_keys():
    """
    Checks if all required API keys and access tokens are present.

    Raises:
        ValueError: If any of the API keys or access tokens is missing.
    """
    if (
        not TWITTER_API_KEY
        or not TWITTER_API_SECRET
        or not TWITTER_ACCESS_TOKEN
        or not TWITTER_ACCESS_TOKEN_SECRET
    ):
        raise ValueError("Please provide Twitter API keys and access tokens.")
    if not OPENAI_API_KEY:
        raise ValueError("Please provide OpenAI API key.")


def setup_tweepy_api():
    """
    Sets up and returns the Tweepy API object using the provided API keys and access tokens.

    Returns:
        tweepy.API: An instance of the Tweepy API object.
    """
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True)


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
            {
                "role": "system",
                "content": "Generate distinct and engaging quotes from well-known tech figures for DevWisdomDaily, an automated Twitter bot that aims to go viral and attract a large audience with its tweets containing relevant hashtags, images, and emojis posted every 12 hours.",
            },
            {
                "role": "assistant",
                "content": f"Here are some previous quotes posted by DevWisdomDaily:\n{previous_quotes_text}",
            },
            {
                "role": "user",
                "content": "Craft a unique, captivating, and concise quote from a notable tech personality, such as a developer, engineer, or software expert, including their name. Make sure the quote differs from previous ones and resonates with the tech community. Add 1-2 relevant hashtags and emojis to increase engagement. Format the quote in a shareable and conversational style: start with the quote itself, followed by the name, and end with an engaging touch.",
            },
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_messages,
            n=1,
            stop=None,
            temperature=0.7,
            max_tokens=60,
        )

        quote = response.choices[0].message["content"].strip()
        quote_text = extract_quote_from_tweet(quote)

        return quote, quote_text


def get_image_examples():
    """
    Return a list of image description examples.

    This function provides a list of textual image descriptions that can be used as examples
    for generating images with DALL-E or any other image generation AI.

    Returns:
        list: A list of strings, each describing a unique and creative image example.
    """
    return [
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
        {
            "role": "system",
            "content": "Your task is to create engaging and visually striking images for Twitter based on quotes, with the goal of making them go viral. Generate detailed descriptions that can be used to create images with DALL-E.",
        },
        {
            "role": "assistant",
            "content": f"Here are some examples of image descriptions to inspire you:\n{example_text}",
        },
        {
            "role": "user",
            "content": f"Directly provide a detailed and creative image description inspired by the quote '{quote_text}', suitable for creating an engaging visual on Twitter, without any introduction.",
        },
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_messages,
        n=1,
        stop=None,
        temperature=0.8,
        max_tokens=250,
    )

    detailed_description = response.choices[0].message["content"].strip()
    return detailed_description


def generate_image(prompt):
    """
    Generates an image URL using OpenAI DALL-E 2 based on the given prompt.

    Args:
        prompt (str): The prompt to generate an image URL.

    Returns:
        str: The image URL generated by DALL-E 2.
    """
    response = openai.Image.create(
        prompt=prompt,
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


def tweet_quote_and_image(API):
    """
    Tweets the given quote and an image generated based on the detailed_description.
    If the tweet fails due to a "Forbidden" error (403), a new quote is generated and the process is retried.

    Args:
        API (tweepy.API): The Tweepy API object.
        quote (str): The quote to be tweeted.
        detailed_description (str): The detailed description for generating an image using DALL-E 2.
    """

    def post_tweet(quote, media_id):
        try:
            API.update_status(status=quote, media_ids=[media_id])
            print(f"Tweeted: {quote}")
            return True
        except tweepy.errors.Forbidden:
            print("Tweeting failed due to forbidden error. Generating a new quote...")
            return False

    try:
        previous_quotes = get_previous_quotes(API)
        previous_quotes_text = "\n".join(previous_quotes)

        while True:
            quote, quote_text = generate_quote(API, previous_quotes_text)
            print(f"Generated quote: {quote}")

            examples = get_image_examples()
            detailed_description = generate_detailed_description(quote_text, examples)
            print(f"Generated detailed description: {detailed_description}")

            image_url = generate_image(detailed_description)
            print(f"Generated image URL: {image_url}")

            media_id = upload_media(image_url, API)
            print(f"Uploaded media ID: {media_id}")

            if post_tweet(quote, media_id):
                break

    except Exception as e:
        handle_error(e)


def handle_error(e):
    """
    Handle various errors that may occur during interaction with the Twitter and OpenAI APIs.

    This function will print an error message based on the type of error encountered, providing
    additional information for API errors and suggesting a solution for unauthorized access.

    Args:
        e (Exception): The exception raised during interaction with the APIs.

    Returns:
        None
    """
    if isinstance(e, tweepy.errors.Unauthorized):
        print(f"An error occurred while interacting with the Twitter API: {e}")
        if e.api_codes and 89 in e.api_codes:  # Invalid or expired token
            print("Please check your Twitter API keys and access tokens.")
    elif isinstance(e, openai.error.APIError):
        print(f"OpenAI API returned an API Error: {e}")
    elif isinstance(e, openai.error.APIConnectionError):
        print(f"Failed to connect to OpenAI API: {e}")
    elif isinstance(e, openai.error.RateLimitError):
        print(f"OpenAI API request exceeded rate limit: {e}")
    else:
        print(f"An unexpected error occurred: {e}")


def trigger_tweet(event, context):
    """
    Triggers the tweet process to generate a quote, a detailed description, and tweet them as an image.

    Args:
        event (dict): A dictionary containing data about the triggering event (not used in this function).
        context (google.cloud.functions.Context): Metadata about the function invocation (not used in this function).
    """
    check_api_keys()
    API = setup_tweepy_api()
    tweet_quote_and_image(API)


def main():
    """
    The main function that triggers the tweet_quote_and_image() function. It sets up the Tweepy API,
    generates a unique quote and its corresponding image description, and tweets them as an image.
    """
    check_api_keys()
    API = setup_tweepy_api()
    tweet_quote_and_image(API)


if __name__ == "__main__":
    main()
