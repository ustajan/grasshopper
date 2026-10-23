"""Filesystem locations used by the GUI.

When the GUI is installed as a package (pip/conda) its own directory is read-only,
so per-user state goes to the platform's config directory instead:
  macOS:  ~/Library/Application Support/grasshopper/
  Linux:  $XDG_CONFIG_HOME/grasshopper/  (default ~/.config/grasshopper/)
"""

import os
import sys
from pathlib import Path


def config_dir() -> Path:
    """Per-user config directory for grasshopper (created on first call)."""
    try:
        from platformdirs import user_config_dir
        base = Path(user_config_dir("grasshopper", appauthor=False))
    except ImportError:
        if sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support" / "grasshopper"
        else:
            base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "grasshopper"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return base


def settings_path() -> Path:
    """Default location of the GUI settings JSON file."""
    return config_dir() / "gui_settings.json"


def icon_file() -> Path:
    """Path to the bundled application icon."""
    try:
        from importlib.resources import files
        return Path(str(files("grasshopper_gui") / "assets" / "icon.png"))
    except Exception:
        return Path(__file__).parent / "assets" / "icon.png"


def package_version() -> str:
    """Installed version of the grasshopper-gui distribution, or 'unknown'."""
    try:
        from importlib.metadata import version
        return version("grasshopper-gui")
    except Exception:
        return "unknown"
