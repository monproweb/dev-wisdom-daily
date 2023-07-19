from config import get_config
import re
from twitter_manager import TwitterManager
from threads_manager import ThreadsManager
from content_generator import ContentGenerator


def trigger_tweet(event, context):
    config = get_config()
    twitter_manager = TwitterManager(config)
    threads_manager = ThreadsManager(config)
    content_generator = ContentGenerator(config)

    previous_quotes = twitter_manager.get_previous_quotes()
    previous_quotes_text = "\n".join(previous_quotes)

    quote, quote_text = content_generator.generate_quote(previous_quotes_text)
    detailed_description = content_generator.generate_detailed_description(quote_text)
    image_url = content_generator.generate_image(detailed_description)

    twitter_manager.tweet_quote_and_image(quote, image_url)
    quote_without_hashtags = re.sub(r"#\S+", "", quote)
    threads_manager.thread_quote_and_image(quote_without_hashtags, image_url)


def main():
    config = get_config()
    twitter_manager = TwitterManager(config)
    threads_manager = ThreadsManager(config)
    content_generator = ContentGenerator(config)

    previous_quotes = twitter_manager.get_previous_quotes()
    previous_quotes_text = "\n".join(previous_quotes)

    quote, quote_text = content_generator.generate_quote(previous_quotes_text)
    detailed_description = content_generator.generate_detailed_description(quote_text)
    image_url = content_generator.generate_image(detailed_description)

    twitter_manager.tweet_quote_and_image(quote, image_url)
    quote_without_hashtags = re.sub(r"#\S+", "", quote)
    threads_manager.thread_quote_and_image(quote_without_hashtags, image_url)


if __name__ == "__main__":
    main()
