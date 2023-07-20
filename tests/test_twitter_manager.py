import pytest
from unittest.mock import patch, MagicMock
from twitter_manager import TwitterManager


@patch("requests.get")
@patch("requests_oauthlib.OAuth1Session")
def test_upload_media(mock_oauth, mock_get):
    config = {
        "TWITTER_API_KEY": "test_key",
        "TWITTER_API_SECRET": "test_secret",
        "TWITTER_ACCESS_TOKEN": "test_token",
        "TWITTER_ACCESS_TOKEN_SECRET": "test_token_secret",
        "TWITTER_BEARER_TOKEN": "test_bearer_token",
    }
    tm = TwitterManager(config)
    mock_get.return_value.content = b"test_data"
    mock_response = MagicMock()
    mock_response.json.return_value = {"media_id_string": "test_media_id"}
    mock_response.status_code = 200
    mock_oauth.return_value.post.return_value = mock_response

    image_url = "http://test_image_url.com"
    assert tm.upload_media(image_url) == "test_media_id"
    mock_get.assert_called_once_with(image_url)
    mock_oauth.return_value.post.assert_called_once()


@patch("requests.get")
@patch("requests_oauthlib.OAuth1Session")
def test_tweet_quote_and_image(mock_oauth, mock_get):
    config = {
        "TWITTER_API_KEY": "test_key",
        "TWITTER_API_SECRET": "test_secret",
        "TWITTER_ACCESS_TOKEN": "test_token",
        "TWITTER_ACCESS_TOKEN_SECRET": "test_token_secret",
        "TWITTER_BEARER_TOKEN": "test_bearer_token",
    }
    tm = TwitterManager(config)
    mock_get.return_value.content = b"test_data"
    mock_upload_response = MagicMock()
    mock_upload_response.json.return_value = {"media_id_string": "test_media_id"}
    mock_upload_response.status_code = 200
    mock_oauth.return_value.post.side_effect = [mock_upload_response, MagicMock()]
    mock_oauth.return_value.post.return_value.status_code = 201

    quote = "#test_quote"
    image_url = "http://test_image_url.com"
    assert tm.tweet_quote_and_image(quote, image_url) == ("test_quote", image_url)
    assert mock_oauth.return_value.post.call_count == 2
