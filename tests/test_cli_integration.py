import subprocess
import sys
from pathlib import Path
import utils


def test_cli_version(tmp_path):
    project_root = Path(__file__).resolve().parent.parent
    cfg_dir = utils.get_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cfg_dir / "config.yaml"
    try:
        cfg_path.write_text("openrouter_api_key: dummykey\nencrypted: false\n")
        result = subprocess.run(
            [sys.executable, str(project_root / "cli.py"), "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "IOP CLI version" in result.stdout
    finally:
        if cfg_path.exists():
            cfg_path.unlink()