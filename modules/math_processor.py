"""Math notation processing module."""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import re


@dataclass
class MathBlock:
    """Represents a math block with its content and formatting."""
    content: str
    delimiter_type: str  # '$$' or '\\['
    indentation: str
    is_inline: bool = False


class MathProcessor:
    """Processes mathematical notation in text."""

    def __init__(self):
        # Regular expressions for math detection
        self.inline_math_pattern = r'\$[^\$]+\$'
        self.display_math_start = re.compile(r'^(\s*)((?:\$\$)|(?:\\\[))\s*$')
        self.display_math_end = re.compile(r'^(\s*)((?:\$\$)|(?:\\\]))\s*$')

    def process_math_blocks(self, lines: List[str]) -> List[str]:
        """Process math blocks in text while preserving indentation."""
        processed_lines = []
        current_block: Optional[MathBlock] = None
        math_content: List[str] = []

        for line in lines:
            if current_block is None:
                # Check for start of math block
                start_match = self.display_math_start.match(line)
                if start_match:
                    indentation, delimiter = start_match.groups()
                    current_block = MathBlock(
                        content="",
                        delimiter_type='$$' if '$$' in delimiter else '\\[',
                        indentation=indentation
                    )
                else:
                    # Process any inline math in the line
                    processed_lines.append(self._process_inline_math(line))
            else:
                # Check for end of math block
                end_match = self.display_math_end.match(line)
                if end_match:
                    # Process the collected math content
                    processed_math = self._process_math_content(
                        math_content,
                        current_block.delimiter_type,
                        current_block.indentation
                    )
                    processed_lines.append(processed_math)
                    current_block = None
                    math_content = []
                else:
                    # Collect math content
                    math_content.append(line)

        # Handle any unclosed math block
        if current_block is not None:
            processed_math = self._process_math_content(
                math_content,
                current_block.delimiter_type,
                current_block.indentation
            )
            processed_lines.append(processed_math)

        return processed_lines

    def _process_math_content(self, content_lines: List[str],
                              delimiter_type: str,
                              indentation: str) -> str:
        """Process the content of a math block."""
        # Clean and join the math content
        cleaned_lines = []
        for line in content_lines:
            # Remove common indentation
            if line.startswith(indentation):
                line = line[len(indentation):]
            # Clean up the line
            line = line.strip()
            if line:
                cleaned_lines.append(line)

        # Join lines with proper spacing
        math_content = " \\\\ ".join(cleaned_lines)

        # Format the final math block
        if delimiter_type == '$$':
            return f"{indentation}$$ {math_content} $$"
        else:
            return f"{indentation}\\[ {math_content} \\]"

    def _process_inline_math(self, line: str) -> str:
        """Process inline math expressions."""

        def replace_math(match: re.Match) -> str:
            # Preserve the math content exactly as is
            return match.group(0)

        return re.sub(self.inline_math_pattern, replace_math, line)

    def is_math_delimiter(self, line: str) -> Tuple[bool, Optional[str]]:
        """Check if a line is a math delimiter and return its type."""
        line = line.strip()
        if line == '$$':
            return True, '$$'
        elif line == '\\[' or line == '\\]':
            return True, '\\['
        return False, None

    def cleanup_math_content(self, content: str) -> str:
        """Clean up math content while preserving structure."""
        # Remove extra spaces but preserve important whitespace
        lines = content.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]

        # Special handling for matrix-like environments
        if any(env in content for env in ['matrix', 'align', 'cases']):
            return " \\\\ ".join(cleaned_lines)

        return " ".join(cleaned_lines)


class MathEnvironments:
    """Constants for various math environments."""

    MATRIX_TYPES = [
        'matrix',
        'pmatrix',
        'bmatrix',
        'Bmatrix',
        'vmatrix',
        'Vmatrix'
    ]

    ALIGNMENT_ENVS = [
        'align',
        'align*',
        'aligned',
        'cases',
        'split'
    ]

    @classmethod
    def is_structured_env(cls, content: str) -> bool:
        """Check if content contains a structured math environment."""
        return any(f"\\begin{{{env}}}" in content
                   for env in cls.MATRIX_TYPES + cls.ALIGNMENT_ENVS)