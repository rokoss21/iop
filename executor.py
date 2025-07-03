import os
import platform
import subprocess
import sys
from typing import Any, Dict

from rich.panel import Panel
from rich.progress import Progress
from rich.syntax import Syntax

import utils
import openrouter


# ----------------------------------------------------------------------------
# Response checks
# ----------------------------------------------------------------------------

def check_for_issue(response: str):
    prefixes = ("извините", "я извиняюсь", "вопрос не ясен", "я")
    if response.lower().startswith(prefixes):
        utils.console.print(Panel(f"[bold yellow]Возникла проблема:[/bold yellow] {response}", title="Предупреждение", border_style="yellow"))
        raise SystemExit(-1)


def check_for_markdown(response: str):
    # Consider code fences as a sign that the model returned formatted text
    if response.count("```") >= 2:
        utils.console.print(Panel("[bold yellow]Предложенная команда содержит разметку, поэтому я не выполнил ответ напрямую:[/bold yellow]", title="Предупреждение", border_style="yellow"))
        syntax = Syntax(response, "markdown", theme="monokai", line_numbers=True)
        utils.console.print(syntax)
        raise SystemExit(-1)


# ----------------------------------------------------------------------------
# User interaction helpers
# ----------------------------------------------------------------------------

def prompt_user_for_action(config: Dict[str, Any], ask_flag: bool, response: str) -> str:
    utils.console.print(Panel(f"[bold cyan]Команда:[/bold cyan] {response}", title="Предложенная команда", border_style="cyan"))

    modify_snippet = " [и]зменить" if config["modify"] else ""
    copy_to_clipboard_snippet = " [к]опировать в буфер обмена"
    create_script_snippet = " [с]крипт"

    if config["safety"] or ask_flag:
        prompt_text = (
            f"[bold]Выполнить команду?[/bold] [green][Д]а[/green] [red][н]ет[/red]{modify_snippet}{copy_to_clipboard_snippet}{create_script_snippet} ==> "
        )
        return utils.console.input(prompt_text)

    return "Д"


# ----------------------------------------------------------------------------
# Script creation
# ----------------------------------------------------------------------------

def create_script(config: Dict[str, Any], query: str, shell: str):
    script_query = (
        f"Создайте скрипт для {query}. Скрипт должен обрабатывать ошибки, предоставлять четкий вывод и работать надежно."
    )
    script_content = openrouter.chat_completion(config, script_query, shell, is_script=True)
    script_name = utils.console.input("[bold cyan]Введите имя скрипта (без расширения):[/bold cyan] ")

    if platform.system() == "Windows":
        script_extension = ".ps1"
        run_command = f"powershell -ExecutionPolicy Bypass -File {script_name}{script_extension}"
    else:
        script_extension = ".sh"
        run_command = f"bash {script_name}{script_extension}"

    script_path = os.path.join(os.getcwd(), f"{script_name}{script_extension}")

    with open(script_path, "w", encoding="utf-8") as script_file:
        script_file.write(script_content)

    if platform.system() != "Windows":
        os.chmod(script_path, 0o755)

    utils.console.print(Panel(f"[bold green]Скрипт создан:[/bold green] {script_path}", title="Успех", border_style="green"))
    utils.console.print(f"[bold cyan]Для запуска скрипта используйте:[/bold cyan] {run_command}")
    return script_path, run_command


# ----------------------------------------------------------------------------
# Command execution pipeline
# ----------------------------------------------------------------------------

def eval_user_intent_and_execute(
    config: Dict[str, Any],
    user_input: str,
    command: str,
    shell: str,
    ask_flag: bool,
    query: str,
):
    if user_input.upper() not in ["", "Д", "К", "И", "С"]:
        utils.console.print("[bold yellow]Действие не выполнено.[/bold yellow]")
        return

    if user_input.upper() in ["Д", ""]:
        try:
            with Progress() as progress:
                task = progress.add_task("[cyan]Выполнение команды...", total=100)
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ["powershell", "-Command", command],
                        shell=True,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                else:
                    result = subprocess.run(
                        ["bash", "-c", command],
                        shell=False,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                progress.update(task, completed=100)
            utils.console.print(Panel(result.stdout, title="Результат выполнения", border_style="green"))
            if result.stderr:
                utils.console.print(Panel(result.stderr, title="Ошибки или предупреждения", border_style="yellow"))
        except subprocess.CalledProcessError as exc:
            utils.console.print(Panel(f"[bold red]Ошибка выполнения команды:[/bold red] {exc}", title="Ошибка", border_style="red"))
            if exc.output:
                utils.console.print(Panel(exc.output, title="Вывод", border_style="yellow"))
            if exc.stderr:
                utils.console.print(Panel(exc.stderr, title="Вывод ошибки", border_style="red"))

    if config["modify"] and user_input.upper() == "И":
        modded_query = utils.console.input("[bold cyan]Измените запрос:[/bold cyan] ")
        modded_response = openrouter.chat_completion(config, modded_query, shell)
        check_for_issue(modded_response)
        check_for_markdown(modded_response)
        user_intent = prompt_user_for_action(config, ask_flag, modded_response)
        utils.console.print()
        eval_user_intent_and_execute(config, user_intent, modded_response, shell, ask_flag, modded_query)

    if user_input.upper() == "К":
        try:
            import pyperclip  # type: ignore

            pyperclip.copy(command)
            utils.console.print("[bold green]Команда скопирована в буфер обмена.[/bold green]")
        except ImportError:
            utils.console.print(
                "[bold red]Не удалось импортировать модуль pyperclip. Убедитесь, что он установлен.[/bold red]"
            )
        except pyperclip.PyperclipException:  # type: ignore[attr-defined]
            utils.console.print(
                "[bold red]Не удалось скопировать в буфер обмена. Убедитесь, что у вас установлены необходимые зависимости.[/bold red]"
            )

    if user_input.upper() == "С":
        script_path, run_command = create_script(config, query, shell)
        utils.console.print(f"[bold cyan]Для запуска скрипта используйте:[/bold cyan] {run_command}")