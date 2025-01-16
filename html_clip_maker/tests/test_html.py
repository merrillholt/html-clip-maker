"""Tests for HTML generation functionality."""

import unittest
from unittest.mock import patch, MagicMock
import pytest
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import re

from modules.html_generator import HTMLGenerator, HTMLTemplate
from modules.config import VERSION, DEFAULT_FONTS


class TestHTMLGenerator(unittest.TestCase):
    """Test suite for HTMLGenerator class."""

    def setUp(self):
        """Set up test cases."""
        self.generator = HTMLGenerator()
        self.test_title = "Test Document"
        self.test_content = "<h1>Test Content</h1>"
        self.template_data = HTMLTemplate(
            title=self.test_title,
            content=self.test_content,
            version=VERSION,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fonts=DEFAULT_FONTS
        )

    def test_generator_initialization(self):
        """Test HTMLGenerator initialization."""
        self.assertIsInstance(self.generator, HTMLGenerator)
        self.assertTrue(hasattr(self.generator, 'template'))

    def test_html_generation_basic(self):
        """Test basic HTML generation."""
        html = self.generator.generate(self.template_data)

        # Parse the generated HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Basic structure tests
        self.assertEqual(soup.title.string, self.test_title)
        self.assertTrue(soup.find('div', id='content'))
        self.assertTrue(soup.find('div', class_='footer'))

        # Check for required scripts and styles
        self.assertTrue(soup.find('script', src=re.compile(r'highlight\.js')))
        self.assertTrue(soup.find('script', src=re.compile(r'mathjax')))
        self.assertTrue(soup.find('link', href=re.compile(r'googleapis\.com')))

    def test_content_wrapping(self):
        """Test content wrapping functionality."""
        test_content = """
        <h1>Title</h1>
        <p>Paragraph</p>
        <h2>Subtitle</h2>
        """
        wrapped = self.generator.wrap_content(test_content)
        soup = BeautifulSoup(wrapped, 'html.parser')

        # Check that non-header elements are wrapped
        self.assertTrue(soup.find('div', class_='content-preserve'))
        # Check that headers are not wrapped
        self.assertEqual(len(soup.find_all('h1')), 1)
        self.assertEqual(len(soup.find_all('h2')), 1)

    def test_custom_styles_application(self):
        """Test application of custom styles."""
        custom_styles = {
            "body": "background-color: #f0f0f0;",
            ".custom-class": "color: red;"
        }
        html = self.generator.generate(self.template_data)
        styled_html = self.generator.apply_custom_styles(html, custom_styles)

        # Check if custom styles are present
        self.assertIn("background-color: #f0f0f0", styled_html)
        self.assertIn("color: red", styled_html)

    @patch('pathlib.Path.write_text')
    def test_html_saving(self, mock_write):
        """Test saving HTML to file."""
        output_path = Path('test.html')
        html_content = "<html>Test</html>"

        self.generator.save(html_content, output_path)
        mock_write.assert_called_once_with(html_content, encoding='utf-8')

    def test_math_configuration(self):
        """Test MathJax configuration in generated HTML."""
        html = self.generator.generate(self.template_data)
        soup = BeautifulSoup(html, 'html.parser')

        # Check MathJax configuration
        mathjax_config = soup.find('script', text=re.compile('MathJax'))
        self.assertIsNotNone(mathjax_config)
        self.assertIn('inlineMath', str(mathjax_config))
        self.assertIn('displayMath', str(mathjax_config))

    def test_version_inclusion(self):
        """Test version information inclusion."""
        html = self.generator.generate(self.template_data)
        self.assertIn(f'v{VERSION}', html)
        self.assertIn(self.template_data.timestamp, html)


@pytest.fixture
def html_generator():
    """Fixture for HTMLGenerator instance."""
    return HTMLGenerator()


@pytest.fixture
def template_data():
    """Fixture for template data."""
    return HTMLTemplate(
        title="Test Document",
        content="<h1>Test Content</h1>",
        version=VERSION,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        fonts=DEFAULT_FONTS
    )


@pytest.mark.parametrize("test_input,expected", [
    ("<h1>Test</h1>", "<h1>Test</h1>"),
    ("<p>Test</p>", '<div class="indent-h1 content-preserve"><p>Test</p></div>'),
    ("Plain text", '<div class="indent-h1 content-preserve">Plain text</div>')
])
def test_content_wrapping_variants(html_generator, test_input, expected):
    """Test content wrapping with different inputs."""
    wrapped = html_generator.wrap_content(test_input)
    assert expected in wrapped


def test_math_rendering_setup(html_generator, template_data):
    """Test setup for math rendering in generated HTML."""
    html = html_generator.generate(template_data)
    soup = BeautifulSoup(html, 'html.parser')

    # Check for MathJax script
    assert soup.find('script', src=re.compile(r'mathjax'))

    # Check for math configuration
    math_config = soup.find('script', text=re.compile('MathJax'))
    assert 'tex' in str(math_config)
    assert 'svg' in str(math_config)


def test_code_highlighting_setup(html_generator, template_data):
    """Test setup for code highlighting in generated HTML."""
    html = html_generator.generate(template_data)
    soup = BeautifulSoup(html, 'html.parser')

    # Check for highlight.js
    assert soup.find('script', src=re.compile(r'highlight\.js'))
    assert soup.find('link', href=re.compile(r'highlight\.js'))


@pytest.mark.integration
class TestHTMLGeneratorIntegration:
    """Integration tests for HTMLGenerator."""

    def test_full_document_generation(self, html_generator, tmp_path):
        """Test complete HTML document generation and saving."""
        test_content = """
        <h1>Test Document</h1>
        <p>Test paragraph with math: $E = mc^2$</p>
        <pre><code class="python">
        def test():
            return "Hello"
        </code></pre>
        """

        template_data = HTMLTemplate(
            title="Integration Test",
            content=test_content,
            version=VERSION,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fonts=DEFAULT_FONTS
        )

        # Generate and save HTML
        html = html_generator.generate(template_data)
        output_path = tmp_path / "test.html"
        html_generator.save(html, output_path)

        # Verify file exists and content
        assert output_path.exists()
        content = output_path.read_text()

        # Check for key components
        assert "<title>Integration Test</title>" in content
        assert "MathJax" in content
        assert "highlight.js" in content
        assert test_content.strip() in content


def test_font_configuration(html_generator):
    """Test font configuration in generated HTML."""
    custom_fonts = {
        'main_font': "'Custom Font', sans-serif",
        'code_font': "'Custom Code Font', monospace",
        'font_size': "18px",
        'line_height': "1.8",
        'code_font_size': "16px"
    }

    template_data = HTMLTemplate(
        title="Font Test",
        content="<p>Test</p>",
        fonts=custom_fonts
    )

    html = html_generator.generate(template_data)

    # Check if custom fonts are applied
    for font_value in custom_fonts.values():
        assert font_value in html


def test_error_handling():
    """Test error handling in HTML generation."""
    generator = HTMLGenerator()

    # Test with invalid template data
    with pytest.raises(AttributeError):
        generator.generate(None)

    # Test with invalid custom styles
    with pytest.raises(TypeError):
        generator.apply_custom_styles("<html></html>", None)


if __name__ == '__main__':
    pytest.main(['-v'])