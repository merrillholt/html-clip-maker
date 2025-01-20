#!/usr/bin/env python3
"""
HTML Clip Maker - Main Program
Converts clipboard content with markdown and math notation to styled HTML
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Dict
import logging
from datetime import datetime

from modules.clipboard import ClipboardManager
from modules.markdown import MarkdownProcessor
from modules.math_processor import MathProcessor
from modules.html_generator import HTMLGenerator, HTMLTemplate
from modules.config import VERSION, DEFAULT_FONTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HTMLClipMaker:
    """Main application class for HTML Clip Maker."""

    def __init__(self):
        self.clipboard = ClipboardManager()
        self.markdown = MarkdownProcessor()
        self.math = MathProcessor()
        self.html_gen = HTMLGenerator()

    def process_content(self, content: str) -> tuple[str, str]:
        """
        Process the input content and return title and processed content.

        Args:
            content: Raw input text

        Returns:
            tuple: (title, processed_content)
        """
        # Split content into lines
        lines = content.strip().split('\n')

        # Extract title from first line
        title = lines[0].lstrip('#').strip()
        content_lines = lines[1:]

        # Process math blocks first
        math_processed = self.math.process_math_blocks(content_lines)

        # Process markdown
        processed_content = self.markdown.process('\n'.join(math_processed))

        return title, processed_content

    def generate_html(self, title: str, content: str,
                      custom_styles: Optional[Dict] = None) -> str:
        """Generate HTML document from processed content."""
        template_data = HTMLTemplate(
            title=title,
            content=self.html_gen.wrap_content(content),
            version=VERSION,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fonts=DEFAULT_FONTS
        )

        html = self.html_gen.generate(template_data)

        if custom_styles:
            html = self.html_gen.apply_custom_styles(html, custom_styles)

        return html

    def save_output(self, html: str, output_path: Path) -> None:
        """Save HTML content to file."""
        try:
            self.html_gen.save(html, output_path)
            logger.info(f"HTML content has been successfully written to {output_path}")
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert clipboard content to styled HTML with math support'
    )
    parser.add_argument(
        'filename',
        help='Base name for output files (without extension)'
    )
    parser.add_argument(
        '--style',
        help='Path to custom CSS file',
        type=Path,
        default=None
    )
    parser.add_argument(
        '--debug',
        help='Enable debug logging',
        action='store_true'
    )
    return parser.parse_args()


def load_custom_styles(style_path: Path) -> Optional[Dict]:
    """Load custom styles from CSS file."""
    if not style_path:
        return None

    try:
        content = style_path.read_text()
        # Simple CSS parser (for basic usage)
        styles = {}
        current_selector = None
        current_properties = []

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.endswith('{'):
                current_selector = line[:-1].strip()
                current_properties = []
            elif line.endswith('}'):
                if current_selector:
                    styles[current_selector] = '\n'.join(current_properties)
                current_selector = None
            else:
                if current_selector:
                    current_properties.append(line)

        return styles
    except Exception as e:
        logger.error(f"Error loading custom styles: {e}")
        return None


def main():
    """Main program entry point."""
    args = parse_arguments()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    try:
        # Initialize application
        app = HTMLClipMaker()

        # Get clipboard content
        logger.debug("Reading clipboard content...")
        content = app.clipboard.get_clipboard_content()
        if not content:
            logger.error("Clipboard is empty")
            sys.exit(1)

        # Process content
        logger.debug("Processing content...")
        title, processed_content = app.process_content(content)

        # Load custom styles if provided
        custom_styles = None
        if args.style:
            logger.debug("Loading custom styles...")
            custom_styles = load_custom_styles(args.style)

        # Generate HTML
        logger.debug("Generating HTML...")
        html = app.generate_html(title, processed_content, custom_styles)

        # Save output
        output_path = Path(args.filename).with_suffix('.html')
        app.save_output(html, output_path)

        # Save original text content
        text_path = Path(args.filename).with_suffix('.txt')
        text_path.write_text(content, encoding='utf-8')
        logger.info(f"Original content saved to {text_path}")

    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            logger.exception("Detailed error information:")
        sys.exit(1)


if __name__ == '__main__':
    main()