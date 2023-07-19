import unittest
from unittest.mock import patch, MagicMock
from twitter_manager import TwitterManager


class TestTwitterManager(unittest.TestCase):
    @patch("requests.get")
    def test_get_previous_quotes(self, mock_get):
        # Arrange
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = (
            '[{"full_text": "First tweet"}, {"full_text": "Second tweet"}]'
        )
        config = {
            "TWITTER_API_KEY": "test_key",
            "TWITTER_API_SECRET": "test_secret",
            "TWITTER_ACCESS_TOKEN": "test_token",
            "TWITTER_ACCESS_TOKEN_SECRET": "test_token_secret",
            "TWITTER_BEARER_TOKEN": "test_bearer_token",
        }
        twitter_manager = TwitterManager(config)

        # Act
        quotes = twitter_manager.get_previous_quotes()

        # Assert
        mock_get.assert_called_once()
        self.assertEqual(len(quotes), 2)

    @patch("requests.get")
    def test_upload_media(self, mock_get):
        # Arrange
        url = "test_url"
        config = {
            "TWITTER_API_KEY": "test_key",
            "TWITTER_API_SECRET": "test_secret",
            "TWITTER_ACCESS_TOKEN": "test_token",
            "TWITTER_ACCESS_TOKEN_SECRET": "test_token_secret",
            "TWITTER_BEARER_TOKEN": "test_bearer_token",
        }
        twitter_manager = TwitterManager(config)

        # Mock successful response from requests.get
        mock_response = MagicMock()
        mock_response.content = b"test"
        mock_get.return_value = mock_response

        # Mock requests.post
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "media_id_string": "test_media_id"
            }

            # Act
            media_id = twitter_manager.upload_media(url)

            # Assert
            mock_get.assert_called_once_with(url)
            mock_post.assert_called()
            self.assertEqual(media_id, "test_media_id")

    @patch("twitter_manager.TwitterManager.upload_media")
    @patch("twitter_manager.OAuth1Session.post")
    def test_tweet_quote_and_image(self, mock_post, mock_upload_media):
        # Arrange
        quote = "test_quote"
        image_url = "test_url"
        config = {
            "TWITTER_API_KEY": "test_key",
            "TWITTER_API_SECRET": "test_secret",
            "TWITTER_ACCESS_TOKEN": "test_token",
            "TWITTER_ACCESS_TOKEN_SECRET": "test_token_secret",
            "TWITTER_BEARER_TOKEN": "test_bearer_token",
        }
        twitter_manager = TwitterManager(config)
        mock_upload_media.return_value = "test_media_id"
        mock_post.return_value.status_code = 201

        # Act
        quote_without_hashtags, url = twitter_manager.tweet_quote_and_image(
            quote, image_url
        )

        # Assert
        mock_upload_media.assert_called_once_with(image_url)
        mock_post.assert_called_once()
        self.assertEqual(quote_without_hashtags, quote)
        self.assertEqual(url, image_url)


if __name__ == "__main__":
    unittest.main()
