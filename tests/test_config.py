import unittest
from unittest.mock import patch
from config import get_config


class TestConfig(unittest.TestCase):
    @patch("os.getenv")
    def test_get_config(self, mock_getenv):
        mock_getenv.return_value = "test_value"

        config = get_config()

        self.assertEqual(config["TWITTER_API_KEY"], "test_value")
        self.assertEqual(config["TWITTER_API_SECRET"], "test_value")
        self.assertEqual(config["TWITTER_ACCESS_TOKEN"], "test_value")
        self.assertEqual(config["TWITTER_ACCESS_TOKEN_SECRET"], "test_value")
        self.assertEqual(config["OPENAI_API_KEY"], "test_value")
        self.assertEqual(config["INSTAGRAM_USERNAME"], "test_value")
        self.assertEqual(config["INSTAGRAM_PASSWORD"], "test_value")


if __name__ == "__main__":
    unittest.main()
