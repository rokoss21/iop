import os
import requests
import yaml
from typing import Any, Dict

from rich.panel import Panel
from rich.progress import Progress

import utils
import prompt


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


def _env_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def update_env_file(api_key: str) -> None:
    """Write or update the local .env with the provided API key."""
    env_path = _env_path()
    if not os.path.exists(env_path):
        with open(env_path, "w") as env_file:
            env_file.write(f"OPENROUTER_API_KEY={api_key}")
        os.chmod(env_path, 0o600)
        return

    utils.console.print("[bold yellow]Файл .env уже существует. Перезаписать?[/bold yellow]")
    if utils.console.input("[bold cyan]Введите Y для перезаписи:[/bold cyan] ").strip().lower() == "y":
        with open(env_path, "w") as env_file:
            env_file.write(f"OPENROUTER_API_KEY={api_key}")
        os.chmod(env_path, 0o600)


def read_config() -> Dict[str, Any]:
    """Load YAML config and resolve env placeholders; ensure API key exists."""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    with open(config_file, "r", encoding="utf-8") as file:
        config: Dict[str, Any] = yaml.safe_load(file)

    # Resolve env key from .env
    env_path = _env_path()
    if not os.path.exists(env_path):
        utils.console.print(Panel("[bold yellow]Файл .env не найден. Пожалуйста, введите API ключ OpenRouter.[/bold yellow]", title="Внимание", border_style="yellow"))
        api_key = get_api_key()
        update_env_file(api_key)
    else:
        import dotenv  # type: ignore

        dotenv.load_dotenv(env_path)

    config["openrouter_api_key"] = os.getenv("OPENROUTER_API_KEY")

    if not config["openrouter_api_key"]:
        utils.console.print(Panel("[bold yellow]API ключ OpenRouter не найден. Пожалуйста, введите его.[/bold yellow]", title="Внимание", border_style="yellow"))
        api_key = get_api_key()
        update_env_file(api_key)
        config["openrouter_api_key"] = api_key

    return config


# ----------------------------------------------------------------------------
# Chat completion
# ----------------------------------------------------------------------------

def chat_completion(config: Dict[str, Any], query: str, shell: str, *, is_script: bool = False) -> str:
    """Send a chat completion request to OpenRouter and return the assistant's reply."""
    if not query:
        utils.console.print(Panel("[bold red]Не указан запрос пользователя.[/bold red]", title="Ошибка", border_style="red"))
        raise SystemExit(-1)

    system_prompt = prompt.get_system_prompt(shell, is_script)

    headers = {
        "Authorization": f"Bearer {config['openrouter_api_key']}",
        "X-Title": config["your_app_name"],
    }

    data = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        "temperature": config["temperature"],
        "max_tokens": config["max_tokens"],
    }

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
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        utils.console.print(Panel("[bold red]Превышено время ожидания ответа от API[/bold red]", title="Ошибка", border_style="red"))
        raise SystemExit(-1)
    except requests.exceptions.RequestException as exc:
        utils.console.print(Panel(f"[bold red]Ошибка при выполнении запроса:[/bold red] {exc}", title="Ошибка", border_style="red"))
        raise SystemExit(-1)