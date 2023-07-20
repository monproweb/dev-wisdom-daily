import pytest
from unittest.mock import patch, MagicMock
from content_generator import ContentGenerator

test_config = {}


def test_generate_quote():
    with patch("content_generator.openai.ChatCompletion.create") as mock_openai, patch(
        "content_generator.get_last_50_quotes"
    ) as mock_get_quotes, patch("content_generator.insert_quote") as mock_insert_quote:
        mock_get_quotes.return_value = ["quote1", "quote2", "quote3"]
        mock_openai.return_value = MagicMock(
            choices=[
                MagicMock(message={"content": '"Test quote" by Test Author #AI #ML'})
            ]
        )

        generator = ContentGenerator(test_config)

        quote, quote_text = generator.generate_quote()

        assert quote == '"Test quote" by Test Author #AI #ML'
        assert quote_text == "Test quote"

        mock_get_quotes.assert_called_once()
        mock_insert_quote.assert_called_once_with("Test quote")


def test_generate_detailed_description():
    with patch("content_generator.openai.ChatCompletion.create") as mock_openai:
        mock_openai.return_value = MagicMock(
            choices=[
                MagicMock(message={"content": "Detailed description of the quote"})
            ]
        )

        generator = ContentGenerator(test_config)
        detailed_description = generator.generate_detailed_description("Test quote")

        assert detailed_description == "Detailed description of the quote"


def test_generate_image():
    with patch("content_generator.openai.Image.create") as mock_openai:
        mock_openai.return_value = MagicMock(
            data=[{"url": "https://example.com/image.png"}]
        )

        generator = ContentGenerator(test_config)
        image_url = generator.generate_image("Test quote")

        assert image_url == "https://example.com/image.png"
