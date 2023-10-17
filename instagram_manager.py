import os
import imaplib
import email
import re
import tempfile
import requests
from PIL import Image
from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice
from instagrapi.exceptions import (
    BadPassword,
    ReloginAttemptExceeded,
    ChallengeRequired,
    SelectContactPointRecoveryForm,
    RecaptchaChallengeForm,
    FeedbackRequired,
    PleaseWaitFewMinutes,
    LoginRequired,
)


class InstagramManager:
    def __init__(self, config):
        self.config = config
        self.client = Client()
        self.client.challenge_code_handler = self.challenge_code_handler
        self.client.handle_exception = self.handle_exception
        self.client.load_settings("session.json")
        self.client.login(
            self.config["INSTAGRAM_USERNAME"], self.config["INSTAGRAM_PASSWORD"]
        )
        self.client.get_timeline_feed()

    def post_on_instagram(self, quote, image_url):
        try:
            with requests.get(image_url, stream=True) as response:
                response.raise_for_status()
                with tempfile.NamedTemporaryFile(
                    suffix=".png", delete=False
                ) as temp_file:
                    for chunk in response.iter_content(1024):
                        temp_file.write(chunk)
                    temp_filename = temp_file.name

            with Image.open(temp_filename) as img:
                jpeg_filename = temp_filename.replace(".png", ".jpeg")
                img.convert("RGB").save(jpeg_filename, "JPEG")

            media = self.client.photo_upload(jpeg_filename, caption=quote)

            os.remove(temp_filename)
            os.remove(jpeg_filename)

            return media
        except Exception as e:
            print(f"An error occurred while posting on Instagram: {e}")
            return None

    def challenge_code_handler(self, username, choice):
        if choice == ChallengeChoice.SMS:
            # handle SMS case if needed
            pass
        elif choice == ChallengeChoice.EMAIL:
            return self.get_code_from_email(username)
        return False

    def get_code_from_email(self, username):
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(self.config["CHALLENGE_EMAIL"], self.config["CHALLENGE_PASSWORD"])
        mail.select("inbox")
        result, data = mail.search(None, "(UNSEEN)")
        assert result == "OK", "Error1 during get_code_from_email: %s" % result
        ids = data.pop().split()
        for num in reversed(ids):
            mail.store(num, "+FLAGS", "\\Seen")  # mark as read
            result, data = mail.fetch(num, "(RFC822)")
            assert result == "OK", "Error2 during get_code_from_email: %s" % result
            msg = email.message_from_string(data[0][1].decode())
            payloads = msg.get_payload()
            if not isinstance(payloads, list):
                payloads = [msg]
            code = None
            for payload in payloads:
                body = payload.get_payload(decode=True).decode()
                if "<div" not in body:
                    continue
                match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
                if not match:
                    continue
                print("Match from email:", match.group(1))
                match = re.search(r">(\d{6})<", body)
                if not match:
                    print('Skip this email, "code" not found')
                    continue
                code = match.group(1)
                if code:
                    return code
        return False

    def handle_exception(self, client, e):
        if isinstance(e, BadPassword):
            client.logger.exception(e)
            client.set_proxy(self.next_proxy().href)
            if client.relogin_attempt > 0:
                self.freeze(str(e), days=7)
                raise ReloginAttemptExceeded(e)
            client.settings = self.rebuild_client_settings()
            return self.update_client_settings(client.get_settings())
        elif isinstance(e, LoginRequired):
            client.logger.exception(e)
            client.relogin()
            return self.update_client_settings(client.get_settings())
        elif isinstance(e, ChallengeRequired):
            api_path = json_value(client.last_json, "challenge", "api_path")
            if api_path == "/challenge/":
                client.set_proxy(self.next_proxy().href)
                client.settings = self.rebuild_client_settings()
            else:
                try:
                    client.challenge_resolve(client.last_json)
                except ChallengeRequired as e:
                    self.freeze("Manual Challenge Required", days=2)
                    raise e
                except (
                    ChallengeRequired,
                    SelectContactPointRecoveryForm,
                    RecaptchaChallengeForm,
                ) as e:
                    self.freeze(str(e), days=4)
                    raise e
                self.update_client_settings(client.get_settings())
            return True
        elif isinstance(e, FeedbackRequired):
            message = client.last_json["feedback_message"]
            if "This action was blocked. Please try again later" in message:
                self.freeze(message, hours=12)
                # client.settings = self.rebuild_client_settings()
                # return self.update_client_settings(client.get_settings())
            elif "We restrict certain activity to protect our community" in message:
                # 6 hours is not enough
                self.freeze(message, hours=12)
            elif "Your account has been temporarily blocked" in message:
                """
                Based on previous use of this feature, your account has been temporarily
                blocked from taking this action.
                This block will expire on 2020-03-27.
                """
                self.freeze(message)
        elif isinstance(e, PleaseWaitFewMinutes):
            self.freeze(str(e), hours=1)
        raise e
