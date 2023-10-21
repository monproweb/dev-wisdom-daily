import os
import tempfile
import requests
from google.cloud import storage
from PIL import Image


class InstagramManager:
    def __init__(self, config):
        self.config = config
        self.access_token = config.get("FACEBOOK_ACCESS_TOKEN")
        self.ig_user_id = config.get("INSTAGRAM_USER_ID")
        self.graph_url = "https://graph.facebook.com/v18.0/"

    def post_on_instagram(self, quote, image_url):
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            with Image.open(response.raw) as img:
                with tempfile.NamedTemporaryFile(
                    suffix=".jpeg", delete=False
                ) as temp_file:
                    img.convert("RGB").save(temp_file, "JPEG")
                    temp_filename = temp_file.name

            gcs_filename = self.upload_to_gcs(temp_filename)
            media = self.publish_to_instagram(gcs_filename, quote)

            if media:
                self.delete_image_from_gcs(gcs_filename)

            os.remove(temp_filename)

            return media
        except Exception as e:
            print(f"An error occurred while posting on Instagram: {e}")
            return None

    def upload_to_gcs(self, file_path):
        storage_client = storage.Client()
        bucket = storage_client.bucket("devwisdomdaily-image")
        filename = os.path.basename(file_path)
        blob = bucket.blob(filename)
        blob.upload_from_filename(file_path)
        return f"https://storage.googleapis.com/devwisdomdaily-image/{filename}"

    def publish_to_instagram(self, image_url, caption):
        url = self.graph_url + self.ig_user_id + "/media"
        params = {
            "access_token": self.access_token,
            "caption": caption,
            "image_url": image_url,
        }
        response = requests.post(url, params=params)
        if response.ok:
            media_id = response.json().get("id")
            return self.publish(media_id)
        else:
            print(f"Failed to upload image: {response.text}")
            return None

    def publish(self, media_id):
        url = self.graph_url + self.ig_user_id + "/media_publish"
        params = {"access_token": self.access_token, "creation_id": media_id}
        response = requests.post(url, params=params)
        if response.ok:
            return response.json()
        else:
            print(f"Failed to publish image: {response.text}")
            return None

    def delete_image_from_gcs(self, url):
        file_name = url.split("/")[-1]
        storage_client = storage.Client()
        bucket = storage_client.bucket("devwisdomdaily-image")
        blob = bucket.blob(file_name)
        blob.delete()
