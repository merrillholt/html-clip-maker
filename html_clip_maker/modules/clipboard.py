"""Clipboard content management module."""

import subprocess
from typing import Optional


class ClipboardManager:
    """Handles clipboard operations for both X11 and Wayland."""

    @staticmethod
    def get_session_type() -> str:
        """Determine the current session type (X11 or Wayland)."""
        try:
            session = subprocess.getoutput("echo $XDG_SESSION_TYPE")
            return session.strip()
        except Exception:
            return "unknown"

    def get_clipboard_content(self) -> Optional[str]:
        """Get content from clipboard based on session type."""
        session_type = self.get_session_type()

        if session_type == "wayland":
            try:
                return subprocess.getoutput("wl-paste")
            except Exception as e:
                raise RuntimeError("wl-clipboard is not installed") from e

        elif session_type == "x11":
            try:
                return subprocess.getoutput("xclip -selection clipboard -o")
            except Exception as e:
                raise RuntimeError("xclip is not installed") from e

        else:
            raise RuntimeError(f"Unsupported session type: {session_type}")