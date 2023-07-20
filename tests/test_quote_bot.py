import pytest
from unittest.mock import MagicMock, patch
from quote_bot import QuoteBot


@patch("quote_bot.TwitterManager")
@patch("quote_bot.ThreadsManager")
@patch("quote_bot.ContentGenerator")
def test_generate_and_post(
    mock_content_generator, mock_threads_manager, mock_twitter_manager
):
    config = {
        "TWITTER_API_KEY": "test_key",
        "TWITTER_API_SECRET": "test_secret",
        "TWITTER_ACCESS_TOKEN": "test_token",
        "TWITTER_ACCESS_TOKEN_SECRET": "test_token_secret",
        "TWITTER_BEARER_TOKEN": "test_bearer_token",
    }

    quote_bot = QuoteBot(config)

    quote = "#test_quote"
    quote_text = "test_quote"
    detailed_description = "test_description"
    image_url = "http://test_image_url.com"
    mock_content_generator.return_value.generate_quote.return_value = (
        quote,
        quote_text,
    )
    mock_content_generator.return_value.generate_detailed_description.return_value = (
        detailed_description
    )
    mock_content_generator.return_value.generate_image.return_value = image_url

    quote_bot.generate_and_post()

    mock_content_generator.return_value.generate_quote.assert_called_once()
    mock_content_generator.return_value.generate_detailed_description.assert_called_once_with(
        quote_text
    )
    mock_content_generator.return_value.generate_image.assert_called_once_with(
        detailed_description
    )
    mock_twitter_manager.return_value.tweet_quote_and_image.assert_called_once_with(
        quote, image_url
    )
    mock_threads_manager.return_value.thread_quote_and_image.assert_called_once_with(
        quote_text, image_url
    )
