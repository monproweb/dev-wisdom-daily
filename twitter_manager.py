import requests
import json
from io import BytesIO
from content_generator import ContentGenerator
import re
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

    def get_previous_quotes(self):
        headers = {"Authorization": f"Bearer {self.config['TWITTER_BEARER_TOKEN']}"}
        screen_name = "DevWisdomDaily"
        url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={screen_name}&count=50&tweet_mode=extended"
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)

        if response.status_code != 200:
            raise Exception(
                f"Request returned an error: {response.status_code}, {response.text}"
            )

        return [self.extract_quote_from_tweet(tweet["full_text"]) for tweet in data]

    def extract_quote_from_tweet(self, tweet):
        match = re.search(r'"(.*?)"', tweet)
        return match.group(1) if match else ""

    def upload_media(self, url):
        response = requests.get(url)
        image_data = BytesIO(response.content).getvalue()

        headers = {
            "Authorization": f"Bearer {self.config['TWITTER_BEARER_TOKEN']}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "command": "INIT",
            "media_type": "image/png",
            "total_bytes": len(image_data),
        }
        init_response = requests.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            headers=headers,
            data=data,
        )
        media_id = init_response.json().get("media_id_string")

        headers["Content-Type"] = "multipart/form-data"
        data = {"command": "APPEND", "media_id": media_id, "segment_index": 0}
        files = {"media": image_data}
        append_response = requests.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            headers=headers,
            data=data,
            files=files,
        )

        if append_response.status_code != 204:
            raise Exception(
                f"Media upload failed at APPEND stage with status code {append_response.status_code}, response {append_response.text}"
            )

        data = {"command": "FINALIZE", "media_id": media_id}
        finalize_response = requests.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            headers=headers,
            data=data,
        )

        if finalize_response.status_code != 200:
            raise Exception(
                f"Media upload failed at FINALIZE stage with status code {finalize_response.status_code}, response {finalize_response.text}"
            )

        return media_id

    def tweet_quote_and_image(self, quote, image_url):
        media_id = self.upload_media(image_url)
        print(f"Uploaded media ID: {media_id}")

        quote_without_hashtags = re.sub(r"#\S+", "", quote)

        payload_v2 = {
            "status": quote,
            "media_ids": media_id,
        }

        response = self.oauth_v1.post(
            "https://api.twitter.com/2/tweets", json=payload_v2
        )

        if response.status_code != 201:
            raise Exception(
                f"Request returned an error: {response.status_code}, {response.text}"
            )

        print(f"Tweeted: {quote}")

        return quote_without_hashtags, image_url
