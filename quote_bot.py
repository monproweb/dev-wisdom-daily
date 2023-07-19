import re
from twitter_manager import TwitterManager
from threads_manager import ThreadsManager
from content_generator import ContentGenerator


class QuoteBot:
    def __init__(self, config):
        self.twitter_manager = TwitterManager(config)
        self.threads_manager = ThreadsManager(config)
        self.content_generator = ContentGenerator(config)

    def generate_and_post(self):
        previous_quotes = self.twitter_manager.get_previous_quotes()
        previous_quotes_text = "\n".join(previous_quotes)

        quote, quote_text = self.content_generator.generate_quote(previous_quotes_text)
        detailed_description = self.content_generator.generate_detailed_description(
            quote_text
        )
        image_url = self.content_generator.generate_image(detailed_description)

        self.twitter_manager.tweet_quote_and_image(quote, image_url)
        quote_without_hashtags = re.sub(r"#\S+", "", quote)

        try:
            self.threads_manager.thread_quote_and_image(
                quote_without_hashtags, image_url
            )
        except Exception as e:
            print(f"An error occurred while threading the quote: {e}")
