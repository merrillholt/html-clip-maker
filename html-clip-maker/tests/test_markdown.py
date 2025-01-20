"""Tests for markdown processing functionality."""

import unittest
import pytest
from textwrap import dedent
from typing import List

from modules.markdown import MarkdownProcessor, MarkdownBlock


class TestMarkdownProcessor(unittest.TestCase):
    """Test suite for MarkdownProcessor class."""

    def setUp(self):
        """Set up test cases."""
        self.processor = MarkdownProcessor()

    def test_headers(self):
        """Test header processing."""
        test_cases = [
            ("# Header 1", "<h1>Header 1</h1>"),
            ("## Header 2", "<h2>Header 2</h2>"),
            ("### Header 3", "<h3>Header 3</h3>"),
            ("#### Header 4", "<h4>Header 4</h4>"),
            ("#Invalid Header", "#Invalid Header"),  # No space after #
            ("# Header with **bold**", "<h1>Header with <strong>bold</strong></h1>")
        ]

        for markdown, expected in test_cases:
            result = self.processor.process(markdown)
            self.assertIn(expected, result)

    def test_emphasis(self):
        """Test emphasis (bold, italic) processing."""
        test_cases = [
            ("**Bold text**", "<strong>Bold text</strong>"),
            ("*Italic text*", "<em>Italic text</em>"),
            ("***Bold italic***", "<strong><em>Bold italic</em></strong>"),
            ("**Bold with *italic* inside**",
             "<strong>Bold with <em>italic</em> inside</strong>"),
            ("~~Strikethrough~~", "<del>Strikethrough</del>")
        ]

        for markdown, expected in test_cases:
            result = self.processor.process(markdown)
            self.assertIn(expected, result)

    def test_code_blocks(self):
        """Test code block processing."""
        markdown = dedent("""
        ```python
        def hello():
            print("Hello, World!")
        ```
        """).strip()

        expected = dedent("""
        <pre><code class="language-python">def hello():
            print("Hello, World!")
        </code></pre>
        """).strip()

        result = self.processor.process(markdown)
        self.assertIn(expected, result)

    def test_inline_code(self):
        """Test inline code processing."""
        test_cases = [
            ("`code`", "<code>code</code>"),
            ("Text with `inline code` here",
             "Text with <code>inline code</code> here"),
            ("Multiple `code` and `more code`",
             "Multiple <code>code</code> and <code>more code</code>")
        ]

        for markdown, expected in test_cases:
            result = self.processor.process(markdown)
            self.assertIn(expected, result)

    def test_lists(self):
        """Test list processing."""
        markdown = dedent("""
        - Item 1
        - Item 2
          - Nested 2.1
          - Nested 2.2
        - Item 3

        1. First
        2. Second
           1. Nested 2.1
           2. Nested 2.2
        3. Third
        """).strip()

        result = self.processor.process(markdown)

        # Check for list elements
        self.assertIn("<ul><li>Item 1</li></ul>", result)
        self.assertIn("<ol><li>First</li></ol>", result)
        self.assertIn("Nested", result)

    def test_blockquotes(self):
        """Test blockquote processing."""
        markdown = dedent("""
        > First line
        > Second line
        > 
        > New paragraph
        """).strip()

        result = self.processor.process(markdown)
        self.assertIn("<blockquote>First line</blockquote>", result)
        self.assertIn("<blockquote>Second line</blockquote>", result)
        self.assertIn("<blockquote>New paragraph</blockquote>", result)

    def test_links(self):
        """Test link processing."""
        test_cases = [
            ("[Link](https://example.com)",
             '<a href="https://example.com">Link</a>'),
            ("https://example.com",
             '<a href="https://example.com">https://example.com</a>'),
            ("[Link with **bold**](https://example.com)",
             '<a href="https://example.com">Link with <strong>bold</strong></a>')
        ]

        for markdown, expected in test_cases:
            result = self.processor.process(markdown)
            self.assertIn(expected, result)

    def test_math_preservation(self):
        """Test preservation of math content."""
        test_cases = [
            ("Inline math: $E = mc^2$", "Inline math: $E = mc^2$"),
            ("$$\nf(x) = x^2\n$$", "$$\nf(x) = x^2\n$$"),
            ("\\[\nx + y = z\n\\]", "\\[\nx + y = z\n\\]")
        ]

        for markdown, expected in test_cases:
            result = self.processor.process(markdown)
            self.assertIn(expected, result)


@pytest.fixture
def markdown_processor():
    """Fixture for MarkdownProcessor instance."""
    return MarkdownProcessor()


@pytest.mark.parametrize("markdown,expected", [
    ("# Test", "<h1>Test</h1>"),
    ("## Test", "<h2>Test</h2>"),
    ("### Test", "<h3>Test</h3>"),
    ("#### Test", "<h4>Test</h4>")
])
def test_header_levels(markdown_processor, markdown, expected):
    """Test different header levels."""
    result = markdown_processor.process(markdown)
    assert expected in result


def test_nested_formatting(markdown_processor):
    """Test nested formatting elements."""
    markdown = "**Bold with *italic* and `code` and $math$**"
    result = markdown_processor.process(markdown)
    assert "<strong>" in result
    assert "<em>" in result
    assert "<code>" in result
    assert "$math$" in result  # Math should be preserved


def test_complex_document(markdown_processor):
    """Test processing of a complex document."""
    markdown = dedent("""
    # Main Title

    ## Section 1

    Text with **bold** and *italic* and `code`.

    - List item 1
    - List item 2
      - Nested item
      - With *formatting*

    > Blockquote with **formatting**
    > And multiple lines

    ```python
    def test():
        return "Hello"
    ```

    Math: $E = mc^2$

    $$
    \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
    $$
    """).strip()

    result = markdown_processor.process(markdown)

    # Check all elements are present
    assert "<h1>Main Title</h1>" in result
    assert "<h2>Section 1</h2>" in result
    assert "<strong>bold</strong>" in result
    assert "<em>italic</em>" in result
    assert "<code>code</code>" in result
    assert "<ul>" in result
    assert "<blockquote>" in result
    assert '<pre><code class="language-python">' in result
    assert "$E = mc^2$" in result
    assert "$$" in result


@pytest.mark.parametrize("test_input,expected", [
    ("- Item", "<ul><li>Item</li></ul>"),
    ("1. Item", "<ol><li>Item</li></ol>"),
    ("* Item", "<ul><li>Item</li></ul>")
])
def test_list_variations(markdown_processor, test_input, expected):
    """Test different list formats."""
    result = markdown_processor.process(test_input)
    assert expected in result


def test_error_handling(markdown_processor):
    """Test error handling in markdown processing."""
    # Test with None input
    with pytest.raises(AttributeError):
        markdown_processor.process(None)

    # Test with empty string
    result = markdown_processor.process("")
    assert result == ""

    # Test with invalid markdown
    result = markdown_processor.process("###No space")
    assert "###No space" in result  # Should remain unchanged


class TestMarkdownBlock:
    """Test suite for MarkdownBlock class."""

    def test_block_creation(self):
        """Test MarkdownBlock instance creation."""
        block = MarkdownBlock(type="header", content="Test", level=1)
        assert block.type == "header"
        assert block.content == "Test"
        assert block.level == 1

    def test_block_defaults(self):
        """Test MarkdownBlock default values."""
        block = MarkdownBlock(type="paragraph", content="Test")
        assert block.level == 0
        assert block.language == ''


if __name__ == '__main__':
    pytest.main(['-v'])