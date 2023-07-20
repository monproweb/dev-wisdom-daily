import pytest
from unittest.mock import patch, MagicMock
import main


def test_trigger_tweet():
    with patch("main.get_config") as mock_get_config, patch(
        "main.QuoteBot"
    ) as mock_quote_bot:
        mock_get_config.return_value = {}
        mock_instance = mock_quote_bot.return_value
        mock_instance.generate_and_post.return_value = None

        main.trigger_tweet(None, None)

        mock_get_config.assert_called_once()
        mock_quote_bot.assert_called_once_with({})
        mock_instance.generate_and_post.assert_called_once()


def test_main():
    with patch("main.get_config") as mock_get_config, patch(
        "main.QuoteBot"
    ) as mock_quote_bot:
        mock_get_config.return_value = {}
        mock_instance = mock_quote_bot.return_value
        mock_instance.generate_and_post.return_value = None

        main.main()

        mock_get_config.assert_called_once()
        mock_quote_bot.assert_called_once_with({})
        mock_instance.generate_and_post.assert_called_once()
