"""Markdown processing module."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import re


@dataclass
class MarkdownBlock:
    """Represents a block-level markdown element."""
    type: str  # 'header', 'list', 'code', 'blockquote', 'paragraph'
    content: str
    level: int = 0  # For headers (1-6) or list nesting level
    language: str = ''  # For code blocks


class MarkdownProcessor:
    """Processes markdown formatting while preserving math blocks."""

    def __init__(self):
        # Block-level patterns
        self.header_pattern = re.compile(r'^(#{1,4})\s+(.+)$')
        self.blockquote_pattern = re.compile(r'^>\s*(.*)$')
        self.list_pattern = re.compile(r'^(\s*)([-*]|\d+\.)\s+(.+)$')
        self.code_block_pattern = re.compile(r'^```(\w*)$')

        # Inline patterns
        self.bold_italic_pattern = re.compile(r'\*\*\*([^*]+)\*\*\*')
        self.bold_pattern = re.compile(r'\*\*([^*]+)\*\*')
        self.italic_pattern = re.compile(r'\*([^*]+)\*')
        self.inline_code_pattern = re.compile(r'`([^`]+)`')
        self.strikethrough_pattern = re.compile(r'~~([^~]+)~~')
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.url_pattern = re.compile(r'(https?://[^\s<]+)')

    def process(self, content: str) -> str:
        """Process markdown content while preserving math blocks."""
        lines = content.split('\n')
        processed_lines = []
        current_block = None
        block_content = []

        for line in lines:
            if current_block is None:
                # Check for new block start
                block = self._identify_block(line)
                if block:
                    current_block = block
                    if block.type == 'code':
                        # Start collecting code block content
                        continue
                    processed_lines.append(self._process_block(block))
                else:
                    # Process as regular line
                    processed_lines.append(self._process_inline(line))
            else:
                # Handle continuing blocks
                if current_block.type == 'code':
                    if line.strip() == '```':
                        # End of code block
                        processed_lines.append(self._format_code_block(
                            block_content,
                            current_block.language
                        ))
                        current_block = None
                        block_content = []
                    else:
                        block_content.append(line)
                    continue

            # Add empty line for readability
            if not line.strip():
                processed_lines.append('<br>')

        return '\n'.join(processed_lines)

    def _identify_block(self, line: str) -> Optional[MarkdownBlock]:
        """Identify the type of markdown block."""
        # Check for headers
        header_match = self.header_pattern.match(line)
        if header_match:
            level = len(header_match.group(1))
            return MarkdownBlock('header', header_match.group(2), level)

        # Check for blockquotes
        blockquote_match = self.blockquote_pattern.match(line)
        if blockquote_match:
            return MarkdownBlock('blockquote', blockquote_match.group(1))

        # Check for code blocks
        code_match = self.code_block_pattern.match(line)
        if code_match:
            return MarkdownBlock('code', '', language=code_match.group(1))

        # Check for lists
        list_match = self.list_pattern.match(line)
        if list_match:
            indent_level = len(list_match.group(1)) // 2
            return MarkdownBlock('list', list_match.group(3), indent_level)

        return None

    def _process_block(self, block: MarkdownBlock) -> str:
        """Process a markdown block into HTML."""
        if block.type == 'header':
            return f'<h{block.level}>{self._process_inline(block.content)}</h{block.level}>'

        if block.type == 'blockquote':
            return f'<blockquote>{self._process_inline(block.content)}</blockquote>'

        if block.type == 'list':
            # Handle both ordered and unordered lists
            is_ordered = bool(re.match(r'\d+\.', block.content))
            list_type = 'ol' if is_ordered else 'ul'
            content = self._process_inline(block.content)
            return f'<{list_type}><li>{content}</li></{list_type}>'

        return self._process_inline(block.content)

    def _process_inline(self, text: str) -> str:
        """Process inline markdown elements while preserving math."""
        # Store math blocks temporarily
        math_blocks = []

        def store_math(match) -> str:
            math_blocks.append(match.group(0))
            return f'MATH_BLOCK_{len(math_blocks) - 1}'

        # Temporarily replace math blocks
        text = re.sub(r'\$[^$]+\$', store_math, text)

        # Process markdown
        text = self.bold_italic_pattern.sub(r'<strong><em>\1</em></strong>', text)
        text = self.bold_pattern.sub(r'<strong>\1</strong>', text)
        text = self.italic_pattern.sub(r'<em>\1</em>', text)
        text = self.inline_code_pattern.sub(r'<code>\1</code>', text)
        text = self.strikethrough_pattern.sub(r'<del>\1</del>', text)
        text = self.link_pattern.sub(r'<a href="\2">\1</a>', text)
        text = self.url_pattern.sub(r'<a href="\1">\1</a>', text)

        # Restore math blocks
        for i, math in enumerate(math_blocks):
            text = text.replace(f'MATH_BLOCK_{i}', math)

        return text

    def _format_code_block(self, lines: List[str], language: str) -> str:
        """Format a code block with syntax highlighting."""
        if not language:
            language = 'plaintext'
        code_content = '\n'.join(lines)
        return f'<pre><code class="language-{language}">{code_content}</code></pre>'

    def process_lists(self, lines: List[str]) -> List[str]:
        """Process lists while maintaining nested structure."""
        processed_lines = []
        current_list_type = None
        list_stack = []

        for line in lines:
            list_match = self.list_pattern.match(line)
            if list_match:
                indent, marker, content = list_match.groups()
                level = len(indent) // 2
                is_ordered = bool(re.match(r'\d+\.', marker))

                # Handle list nesting
                while list_stack and list_stack[-1][0] >= level:
                    _, list_type = list_stack.pop()
                    processed_lines.append(f'</{list_type}>')

                if not list_stack or level > list_stack[-1][0]:
                    list_type = 'ol' if is_ordered else 'ul'
                    list_stack.append((level, list_type))
                    processed_lines.append(f'<{list_type}>')

                processed_lines.append(f'<li>{self._process_inline(content)}</li>')
            else:
                # Close any open lists
                while list_stack:
                    _, list_type = list_stack.pop()
                    processed_lines.append(f'</{list_type}>')
                processed_lines.append(line)

        # Close any remaining lists
        while list_stack:
            _, list_type = list_stack.pop()
            processed_lines.append(f'</{list_type}>')

        return processed_lines