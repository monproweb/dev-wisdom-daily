import requests
import re
import base64
from requests_oauthlib import OAuth1Session


class TwitterManager:
    def __init__(self, config):
        self.config = config
        self.oauth_v1 = OAuth1Session(
            config["TWITTER_API_KEY"],
            config["TWITTER_API_SECRET"],
            resource_owner_key=config["TWITTER_ACCESS_TOKEN"],
            resource_owner_secret=config["TWITTER_ACCESS_TOKEN_SECRET"],
        )

    def upload_media(self, image_url):
        response = requests.get(image_url)
        image_data = base64.b64encode(response.content).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.config['TWITTER_BEARER_TOKEN']}",
        }
        data = {
            "media_data": image_data,
        }

        upload_response = self.oauth_v1.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            headers=headers,
            data=data,
        )

        if upload_response.status_code != 200:
            raise Exception(
                f"Media upload failed with status code {upload_response.status_code}, response {upload_response.text}"
            )

        return upload_response.json().get("media_id_string")

    def tweet_quote_and_image(self, quote, image_url):
        media_id = self.upload_media(image_url)
        print(f"Uploaded media ID: {media_id}")

        quote_without_hashtags = re.sub(r"#\S+", "", quote)

        payload = {"text": quote, "media": {"media_ids": [media_id]}}

        response = self.oauth_v1.post("https://api.twitter.com/2/tweets", json=payload)

        if response.status_code != 201:
            raise Exception(
                f"Request returned an error: {response.status_code}, {response.text}"
            )

        print(f"Tweeted: {quote}")

        return quote_without_hashtags, image_url
