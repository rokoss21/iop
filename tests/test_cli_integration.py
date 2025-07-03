import subprocess
import sys
from pathlib import Path


def test_cli_version(tmp_path):
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"
    try:
        env_path.write_text("OPENROUTER_API_KEY=dummykey")
        result = subprocess.run(
            [sys.executable, str(project_root / "cli.py"), "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "IOP CLI version" in result.stdout
    finally:
        if env_path.exists():
            env_path.unlink()