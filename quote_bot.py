from twitter_manager import TwitterManager
from instagram_manager import InstagramManager
from content_generator import ContentGenerator


class QuoteBot:
    def __init__(self, config):
        self.twitter_manager = TwitterManager(config)
        self.instagram_manager = InstagramManager(config)
        self.content_generator = ContentGenerator(config)

    def generate_and_post(self):
        quote, quote_text = self.content_generator.generate_quote()
        detailed_description = self.content_generator.generate_detailed_description(
            quote_text
        )
        image_url = self.content_generator.generate_image(detailed_description)

        self.instagram_manager.post_on_instagram(quote, image_url)

        self.twitter_manager.tweet_quote_and_image(quote, image_url)
