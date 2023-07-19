import tempfile
import os
import requests
from threads import Threads


def thread_quote_and_image(quote_without_hashtags, image_url, config):
    threads = None
    try:
        threads = Threads(
            username=config["INSTAGRAM_USERNAME"], password=config["INSTAGRAM_PASSWORD"]
        )
    except Exception as e:
        print("An error occurred while setting up Threads: ", e)

    if threads:
        try:
            response = requests.get(image_url, stream=True)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                for chunk in response.iter_content(1024):
                    temp_file.write(chunk)
                temp_filename = temp_file.name

            print(f"Temp file name: {temp_filename}")

            with open(temp_filename, "rb") as image_file:
                created_thread = threads.private_api.create_thread(
                    caption=quote_without_hashtags,
                    image_file=image_file,
                )
            print(f"Posted to Threads: {created_thread}")

            os.remove(temp_filename)

        except Exception as e:
            print("An error occurred while interacting with Threads: ", e)
    else:
        print("Threads was not set up correctly.")
