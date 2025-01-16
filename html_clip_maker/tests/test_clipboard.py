"""Tests for clipboard functionality."""

import unittest
from unittest.mock import patch, MagicMock
import subprocess
import pytest
from modules.clipboard import ClipboardManager


class TestClipboardManager(unittest.TestCase):
    """Test suite for ClipboardManager class."""

    def setUp(self):
        """Set up test cases."""
        self.clipboard_manager = ClipboardManager()
        self.test_content = "Test clipboard content"

    @patch('subprocess.getoutput')
    def test_get_session_type_wayland(self, mock_getoutput):
        """Test session type detection for Wayland."""
        mock_getoutput.return_value = "wayland"
        session_type = self.clipboard_manager.get_session_type()
        self.assertEqual(session_type, "wayland")
        mock_getoutput.assert_called_once_with("echo $XDG_SESSION_TYPE")

    @patch('subprocess.getoutput')
    def test_get_session_type_x11(self, mock_getoutput):
        """Test session type detection for X11."""
        mock_getoutput.return_value = "x11"
        session_type = self.clipboard_manager.get_session_type()
        self.assertEqual(session_type, "x11")
        mock_getoutput.assert_called_once_with("echo $XDG_SESSION_TYPE")

    @patch('subprocess.getoutput')
    def test_get_session_type_unknown(self, mock_getoutput):
        """Test session type detection for unknown session."""
        mock_getoutput.return_value = ""
        session_type = self.clipboard_manager.get_session_type()
        self.assertEqual(session_type, "unknown")

    @patch('subprocess.getoutput')
    def test_get_clipboard_content_wayland(self, mock_getoutput):
        """Test clipboard content retrieval in Wayland."""
        mock_getoutput.side_effect = [
            "wayland",  # session type
            self.test_content  # clipboard content
        ]
        content = self.clipboard_manager.get_clipboard_content()
        self.assertEqual(content, self.test_content)
        self.assertEqual(mock_getoutput.call_count, 2)

    @patch('subprocess.getoutput')
    def test_get_clipboard_content_x11(self, mock_getoutput):
        """Test clipboard content retrieval in X11."""
        mock_getoutput.side_effect = [
            "x11",  # session type
            self.test_content  # clipboard content
        ]
        content = self.clipboard_manager.get_clipboard_content()
        self.assertEqual(content, self.test_content)
        self.assertEqual(mock_getoutput.call_count, 2)

    @patch('subprocess.getoutput')
    def test_wayland_clipboard_not_installed(self, mock_getoutput):
        """Test error handling when wl-clipboard is not installed."""
        mock_getoutput.side_effect = [
            "wayland",
            subprocess.CalledProcessError(1, "wl-paste")
        ]
        with self.assertRaises(RuntimeError) as context:
            self.clipboard_manager.get_clipboard_content()
        self.assertTrue("wl-clipboard is not installed" in str(context.exception))

    @patch('subprocess.getoutput')
    def test_xclip_not_installed(self, mock_getoutput):
        """Test error handling when xclip is not installed."""
        mock_getoutput.side_effect = [
            "x11",
            subprocess.CalledProcessError(1, "xclip")
        ]
        with self.assertRaises(RuntimeError) as context:
            self.clipboard_manager.get_clipboard_content()
        self.assertTrue("xclip is not installed" in str(context.exception))

    @patch('subprocess.getoutput')
    def test_unsupported_session_type(self, mock_getoutput):
        """Test error handling for unsupported session type."""
        mock_getoutput.return_value = "unknown"
        with self.assertRaises(RuntimeError) as context:
            self.clipboard_manager.get_clipboard_content()
        self.assertTrue("Unsupported session type" in str(context.exception))

    @patch('subprocess.getoutput')
    def test_empty_clipboard(self, mock_getoutput):
        """Test handling of empty clipboard content."""
        mock_getoutput.side_effect = [
            "x11",
            ""
        ]
        content = self.clipboard_manager.get_clipboard_content()
        self.assertEqual(content, "")


@pytest.mark.integration
class TestClipboardManagerIntegration:
    """Integration tests for ClipboardManager."""

    @pytest.fixture
    def clipboard_manager(self):
        """Fixture for ClipboardManager instance."""
        return ClipboardManager()

    @pytest.fixture
    def test_content(self):
        """Fixture for test content."""
        return "Test clipboard content for integration tests"

    def test_real_clipboard_operations(self, clipboard_manager, test_content):
        """Test actual clipboard operations.

        Note: This test requires either X11 or Wayland running.
        """
        # Skip if neither X11 nor Wayland is available
        session_type = clipboard_manager.get_session_type()
        if session_type not in ["x11", "wayland"]:
            pytest.skip("Neither X11 nor Wayland is available")

        # Test clipboard content retrieval
        try:
            content = clipboard_manager.get_clipboard_content()
            assert isinstance(content, str)
        except RuntimeError as e:
            if "not installed" in str(e):
                pytest.skip(f"Required clipboard tool is {str(e)}")
            raise

    @pytest.mark.skipif(
        not subprocess.getoutput("echo $XDG_SESSION_TYPE").strip() in ["x11", "wayland"],
        reason="Requires X11 or Wayland"
    )
    def test_clipboard_content_preservation(self, clipboard_manager):
        """Test that clipboard content is preserved correctly."""
        original_content = clipboard_manager.get_clipboard_content()
        try:
            # Test operations here
            assert clipboard_manager.get_clipboard_content() == original_content
        finally:
            # Cleanup would go here if needed
            pass


def test_clipboard_manager_creation():
    """Test ClipboardManager instance creation."""
    manager = ClipboardManager()
    assert isinstance(manager, ClipboardManager)


@pytest.mark.parametrize("session_type,expected_error", [
    ("wayland", "wl-clipboard is not installed"),
    ("x11", "xclip is not installed"),
    ("unknown", "Unsupported session type")
])
def test_clipboard_errors(session_type, expected_error):
    """Test various error conditions with parametrization."""
    with patch('subprocess.getoutput') as mock_getoutput:
        mock_getoutput.return_value = session_type
        manager = ClipboardManager()
        with pytest.raises(RuntimeError) as exc_info:
            if session_type in ["wayland", "x11"]:
                mock_getoutput.side_effect = subprocess.CalledProcessError(1, "")
            manager.get_clipboard_content()
        assert expected_error in str(exc_info.value)


if __name__ == '__main__':
    unittest.main()