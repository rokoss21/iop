import os
import base64
import getpass
import requests
import yaml
from typing import Any, Dict

from rich.panel import Panel
from rich.progress import Progress

import utils
import prompt
from pathlib import Path
import cache
try:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
except ModuleNotFoundError:  # fallback if cryptography not installed yet
    Fernet = None  # type: ignore
    class _DummyInvalidToken(Exception):
        pass
    InvalidToken = _DummyInvalidToken  # type: ignore


VERSION = "1.01"  # keep version accessible for other modules


# ----------------------------------------------------------------------------
# API-key management
# ----------------------------------------------------------------------------

def validate_api_key(api_key: str) -> bool:
    """Validate OpenRouter API key with a simple auth request."""
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Проверка API ключа...", total=100)
            response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers)
            progress.update(task, completed=100)
        return response.status_code == 200
    except requests.exceptions.RequestException as exc:
        utils.console.print(Panel(f"[bold red]Ошибка при валидации API ключа:[/bold red] {exc}", title="Ошибка", border_style="red"))
        return False


def get_api_key() -> str:
    """Interactively ask user for a valid OpenRouter API key."""
    while True:
        api_key = utils.console.input("[bold cyan]Введите ваш API ключ OpenRouter:[/bold cyan] ")
        if validate_api_key(api_key):
            return api_key
        utils.console.print("[bold yellow]Неверный API ключ. Пожалуйста, попробуйте снова.[/bold yellow]")


def _user_config_path() -> Path:
    """Return path to user-specific config file (~/.config/iop/config.yaml on Linux)."""
    cfg_dir = utils.get_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir / "config.yaml"


def _encrypt_api_key(api_key: str, password: str) -> str:
    if Fernet is None:
        utils.console.print("[bold red]Библиотека cryptography не установлена, шифрование недоступно.[/bold red]", markup=True)
        return api_key  # fallback to plain text
    key = base64.urlsafe_b64encode(password.encode("utf-8").ljust(32, b"0")[:32])
    fernet = Fernet(key)
    return fernet.encrypt(api_key.encode("utf-8")).decode("utf-8")


def _decrypt_api_key(token: str, password: str) -> str:
    if Fernet is None:
        return token  # assume plain
    key = base64.urlsafe_b64encode(password.encode("utf-8").ljust(32, b"0")[:32])
    fernet = Fernet(key)
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")


def _write_user_config(content: Dict[str, Any]) -> None:
    path = _user_config_path()
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(content, fh)
    os.chmod(path, 0o600)


def update_user_config_api_key(api_key: str) -> None:
    """Write or update the user config YAML with (optionally encrypted) API key."""
    encrypt_choice = utils.console.input("[bold cyan]Защитить ключ паролем? (Y/N):[/bold cyan] ").strip().lower()
    config_data: Dict[str, Any] = {}
    if encrypt_choice == "y":
        password = getpass.getpass("Введите пароль для шифрования ключа: ")
        enc_key = _encrypt_api_key(api_key, password)
        config_data = {"openrouter_api_key": enc_key, "encrypted": True}
    else:
        config_data = {"openrouter_api_key": api_key, "encrypted": False}

    _write_user_config(config_data)


def read_config() -> Dict[str, Any]:
    """Load default config and merge with user config, ensuring API key available."""
    # Repo default config
    repo_config_file = Path(__file__).with_name("config.yaml")
    with open(repo_config_file, "r", encoding="utf-8") as file:
        config: Dict[str, Any] = yaml.safe_load(file)

    # User-specific overrides
    user_cfg_path = _user_config_path()
    if user_cfg_path.exists():
        with open(user_cfg_path, "r", encoding="utf-8") as fh:
            user_cfg: Dict[str, Any] = yaml.safe_load(fh) or {}
        encrypted = user_cfg.get("encrypted", False)
        if encrypted:
            password = getpass.getpass("Введите пароль для расшифровки API ключа: ")
            try:
                key_plain = _decrypt_api_key(user_cfg["openrouter_api_key"], password)
            except (InvalidToken, KeyError):
                utils.console.print(Panel("[bold red]Неверный пароль расшифровки или повреждённый ключ.[/bold red]", title="Ошибка", border_style="red"))
                raise SystemExit(-1)
            config["openrouter_api_key"] = key_plain
        else:
            config["openrouter_api_key"] = user_cfg.get("openrouter_api_key")
    else:
        utils.console.print(Panel("[bold yellow]Файл конфигурации не найден. Пожалуйста, введите API ключ OpenRouter.[/bold yellow]", title="Внимание", border_style="yellow"))
        api_key = get_api_key()
        update_user_config_api_key(api_key)
        config["openrouter_api_key"] = api_key

    # Fallback final check
    if not config.get("openrouter_api_key"):
        utils.console.print(Panel("[bold red]API ключ OpenRouter не установлен.[/bold red]", title="Ошибка", border_style="red"))
        raise SystemExit(-1)

    return config


# ----------------------------------------------------------------------------
# Chat completion
# ----------------------------------------------------------------------------

def _request_payload(config: Dict[str, Any], system_prompt: str, query: str, stream: bool) -> Dict[str, Any]:
    return {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        "temperature": config["temperature"],
        "max_tokens": config["max_tokens"],
        "stream": stream,
    }


def chat_completion(
    config: Dict[str, Any],
    query: str,
    shell: str,
    *,
    is_script: bool = False,
    stream: bool = False,
) -> str:
    """Send a chat completion request to OpenRouter and return the assistant's reply."""
    if not query:
        utils.console.print(Panel("[bold red]Не указан запрос пользователя.[/bold red]", title="Ошибка", border_style="red"))
        raise SystemExit(-1)

    system_prompt = prompt.get_system_prompt(shell, is_script)

    headers = {
        "Authorization": f"Bearer {config['openrouter_api_key']}",
        "X-Title": config["your_app_name"],
    }

    # Check cache first (only when not script)
    if not is_script:
        cached = cache.get_cached_response(config["model"], query)
        if cached is not None:
            return cached

    data = _request_payload(config, system_prompt, query, stream)

    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Отправка запроса...", total=100)
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30,
            )
            progress.update(task, completed=100)
        response.raise_for_status()
        if stream:
            content_parts: list[str] = []
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith(b"data: "):
                    data_str = line[len(b"data: ") :].decode("utf-8")
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk_json = yaml.safe_load(data_str)
                        delta = chunk_json["choices"][0]["delta"].get("content", "")
                        yield delta  # type: ignore[misc]
                        content_parts.append(delta)
                    except Exception:
                        continue
            full_content = "".join(content_parts)
        else:
            full_content = response.json()["choices"][0]["message"]["content"]

        # Cache full content if eligible
        if not is_script:
            cache.store_response(config["model"], query, full_content)

        return full_content
    except requests.exceptions.Timeout:
        utils.console.print(Panel("[bold red]Превышено время ожидания ответа от API[/bold red]", title="Ошибка", border_style="red"))
        raise SystemExit(-1)
    except requests.exceptions.RequestException as exc:
        utils.console.print(Panel(f"[bold red]Ошибка при выполнении запроса:[/bold red] {exc}", title="Ошибка", border_style="red"))
        raise SystemExit(-1)