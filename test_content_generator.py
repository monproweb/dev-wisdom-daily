import unittest
from unittest.mock import patch
from content_generator import ContentGenerator


class TestContentGenerator(unittest.TestCase):
    def setUp(self):
        self.cg = ContentGenerator()

    @patch("openai.ChatCompletion.create")
    def test_generate_quote(self, mock_create):
        mock_create.return_value = MockResponse(
            choices=[
                MockMessage(
                    {"content": '"This is a test quote." - Test Person #Test 🎉'}
                )
            ]
        )
        quote, quote_text = self.cg.generate_quote("Test previous quote")
        self.assertEqual(quote, '"This is a test quote." - Test Person #Test 🎉')
        self.assertEqual(quote_text, "This is a test quote.")

    @patch("openai.ChatCompletion.create")
    def test_generate_detailed_description(self, mock_create):
        mock_create.return_value = MockResponse(
            choices=[MockMessage({"content": "This is a detailed description."})]
        )
        detailed_description = self.cg.generate_detailed_description("Test quote")
        self.assertEqual(detailed_description, "This is a detailed description.")

    @patch("openai.Image.create")
    def test_generate_image(self, mock_create):
        mock_create.return_value = MockImageResponse(
            data=[{"url": "https://monproweb.eth.limo/test.png"}]
        )
        image_url = self.cg.generate_image("Test prompt")
        self.assertEqual(image_url, "http://monproweb.eth.limo/test.png")


class MockResponse:
    def __init__(self, choices):
        self.choices = choices


class MockMessage:
    def __init__(self, message):
        self.message = message


class MockImageResponse:
    def __init__(self, data):
        self.data = data


if __name__ == "__main__":
    unittest.main()
