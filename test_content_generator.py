import unittest
from unittest.mock import patch, MagicMock
from content_generator import ContentGenerator


class TestContentGenerator(unittest.TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.content_generator = ContentGenerator(self.api)

    @patch("openai.ChatCompletion.create")
    def test_generate_quote(self, mock_chat_create):
        # Define a list of mock responses
        mock_responses = [
            MagicMock(
                choices=[
                    MagicMock(
                        message={
                            "content": '"Test quote" - Test Author 💻🚀 #Test1 #Test2'
                        }
                    )
                ]
            ),
            MagicMock(choices=[MagicMock(message={"content": "No quote here"})]),
            MagicMock(choices=[]),
        ]

        # Define a list of expected results
        expected_results = [
            ('"Test quote" - Test Author 💻🚀 #Test1 #Test2', '"Test quote"'),
            ("No quote here", ""),
            ("", ""),
        ]

        # Test generate_quote with each mock response and check the result
        for mock_response, expected_result in zip(mock_responses, expected_results):
            mock_chat_create.return_value = mock_response
            result = self.content_generator.generate_quote()
            self.assertEqual(result, expected_result)

    # Add more tests...


if __name__ == "__main__":
    unittest.main()
