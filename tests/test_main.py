import unittest
from unittest.mock import patch, MagicMock
import main


class TestMain(unittest.TestCase):
    @patch("main.get_config")
    @patch("main.TwitterManager")
    @patch("main.ThreadsManager")
    @patch("main.ContentGenerator")
    def test_trigger_tweet(
        self,
        mock_ContentGenerator,
        mock_ThreadsManager,
        mock_TwitterManager,
        mock_get_config,
    ):
        mock_get_config.return_value = {
            "OPENAI_API_KEY": "test_key",
            "TWITTER_BEARER_TOKEN": "test_bearer_token",
        }

        main.trigger_tweet(None, None)

        mock_get_config.assert_called_once()
        mock_TwitterManager.assert_called_once_with(
            mock_get_config.return_value, "test_bearer_token"
        )
        mock_ThreadsManager.assert_called_once_with(mock_get_config.return_value)
        mock_ContentGenerator.assert_called_once()

        mock_TwitterManager.return_value.tweet_quote_and_image.assert_called_once_with(
            mock_ContentGenerator.return_value
        )
        mock_ThreadsManager.return_value.thread_quote_and_image.assert_called_once()

    @patch("main.get_config")
    @patch("main.TwitterManager")
    @patch("main.ThreadsManager")
    @patch("main.ContentGenerator")
    def test_main(
        self,
        mock_ContentGenerator,
        mock_ThreadsManager,
        mock_TwitterManager,
        mock_get_config,
    ):
        mock_get_config.return_value = {
            "OPENAI_API_KEY": "test_key",
            "TWITTER_BEARER_TOKEN": "test_bearer_token",
        }

        main.main()

        mock_get_config.assert_called_once()
        mock_TwitterManager.assert_called_once_with(
            mock_get_config.return_value, "test_bearer_token"
        )
        mock_ThreadsManager.assert_called_once_with(mock_get_config.return_value)
        mock_ContentGenerator.assert_called_once()

        mock_TwitterManager.return_value.tweet_quote_and_image.assert_called_once_with(
            mock_ContentGenerator.return_value
        )
        mock_ThreadsManager.return_value.thread_quote_and_image.assert_called_once()


if __name__ == "__main__":
    unittest.main()
