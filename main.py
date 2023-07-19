from config import get_config
from quote_bot import QuoteBot


def trigger_tweet(event, context):
    config = get_config()
    quote_bot = QuoteBot(config)
    quote_bot.generate_and_post()


def main():
    config = get_config()
    quote_bot = QuoteBot(config)
    quote_bot.generate_and_post()


if __name__ == "__main__":
    main()
