import os
import platform
import logging
from rich.console import Console
from typing import Any

# Initialize Rich Console globally so other modules can reuse it
console = Console()

# Detect if running inside Windows cmd.exe for correct newlines
IS_CMD = os.environ.get("TERM") == "xterm" or "cmd" in os.environ.get("COMSPEC", "").lower()

# Configure basic logging once
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def safe_print(*args: Any, **kwargs: Any) -> None:
    """Wrapper around Console.print that adds an extra newline for cmd.exe."""
    console.print(*args, **kwargs)
    if IS_CMD:
        console.print()  # Extra empty line for CMD


def reset_console() -> None:
    """Reset terminal colours for the current platform."""
    if platform.system() == "Windows":
        os.system("color")
    else:
        # ANSI reset
        print("\033[0m", end="", flush=True)


def get_os_friendly_name() -> str:
    """Return a human-readable name for the current operating system."""
    os_name = platform.system()
    if os_name == "Linux":
        try:
            import distro  # type: ignore

            return f"Linux/{distro.name(pretty=True)}"
        except ModuleNotFoundError:
            # Fall back if distro is not installed
            return "Linux"
    elif os_name == "Darwin":
        return "Darwin/macOS"
    else:
        return os_name