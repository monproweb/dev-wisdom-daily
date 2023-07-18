import re
import openai
import requests
import json


class ContentGenerator:
    def __init__(self, bearer_token):
        """
        Initialize the ContentGenerator with a Bearer token.

        Args:
            bearer_token (str): The Bearer token for Twitter API.
        """
        self.bearer_token = bearer_token

    def get_user_id(self, username):
        """
        Fetches the user ID from the specified Twitter account.

        Args:
            username (str): The username of the Twitter account.

        Returns:
            str: The user ID of the Twitter account.
        """
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)

        if response.status_code != 200:
            raise Exception(
                f"Request returned an error: {response.status_code}, {response.text}"
            )

        return data["data"]["id"]

    def get_previous_quotes(self):
        """
        Fetches the latest tweets from the specified Twitter account and extracts the quotes from them.

        This method uses the Twitter API to fetch the most recent tweets from the "@DevWisdomDaily" account.
        It then uses the `extract_quote_from_tweet` method to extract the quote from each tweet text.

        Returns:
            list[str]: A list of quotes extracted from the last 50 tweets.
        """
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        user_id = self.get_user_id("DevWisdomDaily")
        url = f"https://api.twitter.com/2/users/{user_id}/tweets?tweet.fields=created_at,text&max_results=50"
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)

        if response.status_code != 200:
            raise Exception(
                f"Request returned an error: {response.status_code}, {response.text}"
            )

        return [self.extract_quote_from_tweet(tweet["text"]) for tweet in data["data"]]

    def extract_quote_from_tweet(self, tweet):
        """
        Extract the quote text from a given tweet text.

        Args:
            tweet (str): The text of the tweet containing the quote.

        Returns:
            str: The extracted quote text.
        """
        match = re.search(r'"(.*?)"', tweet)
        return match.group(1) if match else ""

    def generate_quote(self, previous_quotes_text):
        """
        Generate a developer quote using OpenAI GPT-4.

        Returns:
            tuple: A tuple containing the generated quote formatted for a tweet and the extracted quote text.
        """
        chat_messages = [
            {
                "role": "assistant",
                "content": f"Here are some previous quotes posted by DevWisdomDaily:\n{previous_quotes_text}",
            },
            {
                "role": "user",
                "content": "Share a thought-provoking and concise quote that captures the spirit of a specific domain within the tech industry, such as artificial intelligence, web3 development, software development, game development, cybersecurity, or data science. The quote should come from a respected figure in the specified domain and resonate within the tech community. Use 1-2 relevant hashtags and emojis to enhance engagement. Present the quote first, followed by the individual's name and emojis, and end with the appropriate hashtags.",
            },
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=chat_messages,
            n=1,
            stop=None,
            temperature=0.7,
            max_tokens=60,
        )

        if response.choices:
            quote = response.choices[0].message["content"].strip()
            quote_text = self.extract_quote_from_tweet(quote)
            return quote, quote_text

        return "", ""

    def generate_detailed_description(self, quote_text):
        """
        Generate a detailed description for an image using OpenAI GPT-4 based on the given quote_text.

        Args:
            quote_text (str): The quote text to base the image description on.

        Returns:
            str: The detailed description for generating an image using DALL-E 2.
        """
        chat_messages = [
            {
                "role": "user",
                "content": f"Imagine a vivid and intricate visual representation that is deeply inspired by the quote \"{quote_text}\". This image should be rich in detail, allowing for a comprehensive exploration of the quote's meaning and emotion. Incorporate various adjectives, locations, or artistic styles to enhance the image's depth and appeal. Additionally, consider infusing the image with surreal or fantastical elements to make it even more captivating. Your goal is to create a scene or metaphor that is both imaginative and engaging, drawing the viewer into a world that reflects the essence of the quote.",
            },
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=chat_messages,
            n=1,
            stop=None,
            temperature=0.8,
            max_tokens=150,
        )

        detailed_description = response.choices[0].message["content"].strip()
        return detailed_description

    def generate_image(self, prompt):
        """
        Generate an image URL using DALL-E based on the given prompt.

        Args:
            prompt (str): The prompt to generate an image URL.

        Returns:
            str: The image URL generated by DALL-E.
        """
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url",
        )

        image_url = response.data[0]["url"]
        return image_url
