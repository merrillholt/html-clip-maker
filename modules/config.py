"""Configuration settings and constants."""

VERSION = "1.0.0"

# HTML Template settings
HIGHLIGHT_JS_VERSION = "10.0.3"
MATHJAX_VERSION = "3"

# Font settings
DEFAULT_FONTS = {
    'main_font': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif",
    'code_font': "'Fira Code', 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace",
    'font_size': "16px",
    'line_height': "1.6",
    'code_font_size': "14px"
}

# Math delimiters
INLINE_MATH_DELIMITERS = ['$', '$']
DISPLAY_MATH_DELIMITERS = [['$$', '$$'], ['\\[', '\\]']]

# File extensions
DEFAULT_OUTPUT_EXT = '.html'
DEFAULT_TEXT_EXT = '.txt'