import unittest
from unittest.mock import patch, MagicMock
from threads_manager import ThreadsManager


class TestThreadsManager(unittest.TestCase):
    @patch("requests.get")
    @patch("tempfile.NamedTemporaryFile")
    @patch("os.remove")
    @patch("threads_manager.Threads")
    def test_thread_quote_and_image(
        self, mock_Threads, mock_remove, mock_NamedTemporaryFile, mock_get
    ):
        config = {
            "INSTAGRAM_USERNAME": "test_username",
            "INSTAGRAM_PASSWORD": "test_password",
        }
        image_url = "test_url"
        quote_without_hashtags = "test_quote"

        # Mock successful response from requests.get
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"test"]
        mock_get.return_value = mock_response

        # Mock successful temp file creation
        temp_file_mock = MagicMock()
        mock_NamedTemporaryFile.return_value.__enter__.return_value = temp_file_mock

        # Mock successful thread creation
        threads_instance_mock = MagicMock()
        mock_Threads.return_value = threads_instance_mock

        threads_manager = ThreadsManager(config)
        threads_manager.thread_quote_and_image(quote_without_hashtags, image_url)

        # Verify the calls were made correctly
        mock_get.assert_called_once_with(image_url, stream=True)
        mock_NamedTemporaryFile.assert_called_once_with(suffix=".png", delete=False)
        temp_file_mock.write.assert_called_once_with(b"test")
        threads_instance_mock.private_api.create_thread.assert_called_once()

        # Test when Threads raises an exception
        mock_Threads.side_effect = Exception("Test Exception")

        threads_manager = ThreadsManager(config)
        self.assertIsNone(threads_manager.threads)


if __name__ == "__main__":
    unittest.main()
