import os
from typing import Optional

from rich.panel import Panel
from rich.table import Table

import utils


def get_system_prompt(shell: str, is_script: bool = False) -> str:
    """Return system prompt text filled with dynamic placeholders.

    Parameters
    ----------
    shell: str
        Name of the shell (`bash`, `powershell`, ...)
    is_script: bool, optional
        If True – adds additional instructions for script generation.
    """
    prompt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.txt")
    with open(prompt_file, "r", encoding="utf-8") as file:
        system_prompt = file.read()

    system_prompt = system_prompt.replace("{shell}", shell)
    system_prompt = system_prompt.replace("{os}", utils.get_os_friendly_name())

    if is_script:
        system_prompt += "\n\nПри создании скрипта следуйте этим дополнительным рекомендациям:"
        system_prompt += "\n* Создайте надежный скрипт, который обрабатывает потенциальные ошибки и предоставляет информативные сообщения об ошибках"
        system_prompt += f"\n* Для {utils.get_os_friendly_name()} используйте соответствующие механизмы обработки ошибок"
        system_prompt += "\n* При работе с USB-устройствами или системными событиями используйте несколько методов для обеспечения надежных результатов"
        system_prompt += "\n* Включите комментарии, объясняющие назначение каждого основного раздела скрипта"
        system_prompt += "\n* Всегда включайте способ четкого отображения результатов пользователю"

    return system_prompt


def ensure_prompt_is_question(prompt: str) -> str:
    """Guarantee that the prompt ends with a question mark or period.

    Raises
    ------
    ValueError
        If the prompt is empty or consists solely of whitespace.
    """
    if not prompt.strip():
        raise ValueError("Запрос не должен быть пустым.")
    if prompt[-1:] not in ["?", "."]:
        prompt += "?"
    return prompt


def print_usage(config):
    """Pretty usage message leveraging Rich tables and panels."""
    utils.console.print(Panel("[bold cyan]Разработчик @rokoss21, версия 1.0[/bold cyan]", border_style="cyan"))
    utils.console.print()
    utils.console.print("[bold]Использование:[/bold] iop [-a] [-k] <ваш вопрос или команда>")
    utils.console.print("[bold]Аргументы:[/bold]")
    utils.console.print("  [cyan]-a, --ask:[/cyan] Запрашивать подтверждение перед выполнением команды")
    utils.console.print("  [cyan]-k, --key:[/cyan] Изменить API ключ OpenRouter")
    utils.console.print()

    table = Table(title="Текущая конфигурация")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="magenta")
    for key, value in config.items():
        if key != "openrouter_api_key":
            table.add_row(key.capitalize(), str(value))
    utils.console.print(table)