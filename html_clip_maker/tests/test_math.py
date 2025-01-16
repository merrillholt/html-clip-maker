"""Tests for mathematical notation processing functionality."""

import unittest
import pytest
from textwrap import dedent
from modules.math_processor import MathProcessor, MathBlock, MathEnvironments


class TestMathProcessor(unittest.TestCase):
    """Test suite for MathProcessor class."""

    def setUp(self):
        """Set up test cases."""
        self.processor = MathProcessor()

    def test_inline_math(self):
        """Test inline math processing."""
        test_cases = [
            ("Simple: $x + y$", "Simple: $x + y$"),
            ("Multiple: $a + b$ and $c + d$", "Multiple: $a + b$ and $c + d$"),
            ("With spaces: $ x + y $", "With spaces: $ x + y $"),
            ("Escaped: \\$not math\\$", "Escaped: \\$not math\\$")
        ]

        for input_text, expected in test_cases:
            result = self.processor._process_inline_math(input_text)
            self.assertEqual(result, expected)

    def test_display_math_dollars(self):
        """Test display math with $$ delimiters."""
        test_cases = [
            # Simple equation
            ("""
            $$
            x = y + z
            $$
            """, "$$ x = y + z $$"),

            # Matrix
            ("""
            $$
            \\begin{matrix}
            a & b \\\\
            c & d
            \\end{matrix}
            $$
            """, "$$ \\begin{matrix} a & b \\\\ c & d \\end{matrix} $$"),

            # Aligned equations
            ("""
            $$
            \\begin{align}
            x &= a + b \\\\
            y &= c + d
            \\end{align}
            $$
            """, "$$ \\begin{align} x &= a + b \\\\ y &= c + d \\end{align} $$")
        ]

        for input_text, expected in test_cases:
            result = '\n'.join(self.processor.process_math_blocks(
                dedent(input_text).strip().split('\n')))
            self.assertIn(expected, result)

    def test_display_math_brackets(self):
        """Test display math with \[ \] delimiters."""
        test_cases = [
            # Simple equation
            ("""
            \\[
            x = y + z
            \\]
            """, "\\[ x = y + z \\]"),

            # Integration
            ("""
            \\[
            \\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
            \\]
            """, "\\[ \\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2} \\]")
        ]

        for input_text, expected in test_cases:
            result = '\n'.join(self.processor.process_math_blocks(
                dedent(input_text).strip().split('\n')))
            self.assertIn(expected, result)

    def test_indented_math(self):
        """Test math blocks with indentation."""
        test_cases = [
            # List item with math
            ("""
            1. Item with math:
               $$
               x = y + z
               $$
            """, "   $$ x = y + z $$"),

            # Blockquote with math
            ("""
            > Math in quote:
            > \\[
            > E = mc^2
            > \\]
            """, "> \\[ E = mc^2 \\]")
        ]

        for input_text, expected in test_cases:
            result = '\n'.join(self.processor.process_math_blocks(
                dedent(input_text).strip().split('\n')))
            self.assertIn(expected, result)

    def test_special_environments(self):
        """Test special math environments."""
        test_cases = [
            # Cases environment
            ("""
            $$
            \\begin{cases}
            x + y = 1 \\\\
            x - y = 0
            \\end{cases}
            $$
            """, "$$ \\begin{cases} x + y = 1 \\\\ x - y = 0 \\end{cases} $$"),

            # Aligned equations
            ("""
            $$
            \\begin{align*}
            x &= a + b \\\\
            y &= c + d
            \\end{align*}
            $$
            """, "$$ \\begin{align*} x &= a + b \\\\ y &= c + d \\end{align*} $$")
        ]

        for input_text, expected in test_cases:
            result = '\n'.join(self.processor.process_math_blocks(
                dedent(input_text).strip().split('\n')))
            self.assertIn(expected, result)


@pytest.fixture
def math_processor():
    """Fixture for MathProcessor instance."""
    return MathProcessor()


@pytest.mark.parametrize("input_text,expected", [
    # Inline math
    ("$x + y$", "$x + y$"),
    ("$\\frac{1}{2}$", "$\\frac{1}{2}$"),

    # Display math with $$
    ("$$ x + y $$", "$$ x + y $$"),
    ("$$ \\frac{1}{2} $$", "$$ \\frac{1}{2} $$"),

    # Display math with \[ \]
    ("\\[ x + y \\]", "\\[ x + y \\]"),
    ("\\[ \\frac{1}{2} \\]", "\\[ \\frac{1}{2} \\]")
])
def test_math_preservation(math_processor, input_text, expected):
    """Test preservation of math content."""
    result = '\n'.join(math_processor.process_math_blocks([input_text]))
    assert expected in result


def test_nested_structures(math_processor):
    """Test handling of nested mathematical structures."""
    input_text = dedent("""
    $$
    \\begin{cases}
        x + y = 1 & \\text{if } x > 0 \\\\
        \\begin{pmatrix}
            a & b \\\\
            c & d
        \\end{pmatrix} & \\text{otherwise}
    \\end{cases}
    $$
    """).strip()

    result = '\n'.join(math_processor.process_math_blocks(input_text.split('\n')))
    assert '\\begin{cases}' in result
    assert '\\begin{pmatrix}' in result
    assert '\\end{cases}' in result
    assert '\\end{pmatrix}' in result


def test_math_block_class():
    """Test MathBlock class functionality."""
    block = MathBlock(
        content="x + y = z",
        delimiter_type="$$",
        indentation="    ",
        is_inline=False
    )
    assert block.content == "x + y = z"
    assert block.delimiter_type == "$$"
    assert block.indentation == "    "
    assert not block.is_inline


def test_math_environments():
    """Test MathEnvironments class functionality."""
    # Test matrix types
    assert 'matrix' in MathEnvironments.MATRIX_TYPES
    assert 'bmatrix' in MathEnvironments.MATRIX_TYPES
    assert 'pmatrix' in MathEnvironments.MATRIX_TYPES

    # Test alignment environments
    assert 'align' in MathEnvironments.ALIGNMENT_ENVS
    assert 'align*' in MathEnvironments.ALIGNMENT_ENVS
    assert 'cases' in MathEnvironments.ALIGNMENT_ENVS

    # Test environment detection
    content = "\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}"
    assert MathEnvironments.is_structured_env(content)


@pytest.mark.parametrize("environment", [
    "matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix",
    "align", "align*", "aligned", "cases", "split"
])
def test_math_environments_recognition(environment):
    """Test recognition of different math environments."""
    content = f"\\begin{{{environment}}} content \\end{{{environment}}}"
    assert MathEnvironments.is_structured_env(content)


def test_error_handling(math_processor):
    """Test error handling in math processing."""
    # Test unclosed delimiters
    input_text = "$$\nx + y\n"  # Missing closing $$
    result = '\n'.join(math_processor.process_math_blocks(input_text.split('\n')))
    assert 'x + y' in result

    # Test mismatched delimiters
    input_text = "$$\nx + y\n\\]"  # Opening $$ with closing \]
    result = '\n'.join(math_processor.process_math_blocks(input_text.split('\n')))
    assert 'x + y' in result


if __name__ == '__main__':
    pytest.main(['-v'])