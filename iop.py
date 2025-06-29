#!/usr/bin/env python3

import os
import platform
import sys
import subprocess
import requests
import yaml
import logging
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.syntax import Syntax

VERSION = "1.01"

# Инициализация Rich Console
console = Console()

# Определение типа терминала
IS_CMD = os.environ.get('TERM') == 'xterm' or 'cmd' in os.environ.get('COMSPEC', '').lower()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def safe_print(*args, **kwargs):
    console.print(*args, **kwargs)
    if IS_CMD:
        console.print()  # Добавляем дополнительную пустую строку для CMD

def reset_console():
    if platform.system() == "Windows":
        os.system("color")
    else:
        print("\033[0m", end="", flush=True)

def validate_api_key(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Проверка API ключа...", total=100)
            response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers)
            progress.update(task, completed=100)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        console.print(Panel(f"[bold red]Ошибка при валидации API ключа:[/bold red] {e}", title="Ошибка", border_style="red"))
        return False

def get_api_key():
    while True:
        api_key = console.input("[bold cyan]Введите ваш API ключ OpenRouter:[/bold cyan] ")
        if validate_api_key(api_key):
            return api_key
        console.print("[bold yellow]Неверный API ключ. Пожалуйста, попробуйте снова.[/bold yellow]")

def update_env_file(api_key):
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w") as env_file:
            env_file.write(f"OPENROUTER_API_KEY={api_key}")
        os.chmod(env_path, 0o600)  # Устанавливаем права доступа только для владельца
    else:
        console.print("[bold yellow]Файл .env уже существует. Перезаписать?[/bold yellow]")
        if console.input("[bold cyan]Введите Y для перезаписи:[/bold cyan] ").strip().lower() == "y":
            with open(env_path, "w") as env_file:
                env_file.write(f"OPENROUTER_API_KEY={api_key}")
            os.chmod(env_path, 0o600)  # Обновляем права доступа только для владельца

def read_config():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        console.print(Panel("[bold yellow]Файл .env не найден. Пожалуйста, введите API ключ OpenRouter.[/bold yellow]", title="Внимание", border_style="yellow"))
        api_key = get_api_key()
        update_env_file(api_key)
    else:
        import dotenv
        dotenv.load_dotenv(env_path)
    
    config['openrouter_api_key'] = os.getenv('OPENROUTER_API_KEY')
    
    if not config['openrouter_api_key']:
        console.print(Panel("[bold yellow]API ключ OpenRouter не найден. Пожалуйста, введите его.[/bold yellow]", title="Внимание", border_style="yellow"))
        api_key = get_api_key()
        update_env_file(api_key)
        config['openrouter_api_key'] = api_key
    
    return config

def get_system_prompt(shell, is_script=False):
    prompt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.txt")
    with open(prompt_file, "r", encoding="utf-8") as file:
        system_prompt = file.read()
    
    system_prompt = system_prompt.replace("{shell}", shell)
    system_prompt = system_prompt.replace("{os}", get_os_friendly_name())
    
    if is_script:
        system_prompt += "\n\nПри создании скрипта следуйте этим дополнительным рекомендациям:"
        system_prompt += "\n* Создайте надежный скрипт, который обрабатывает потенциальные ошибки и предоставляет информативные сообщения об ошибках"
        system_prompt += f"\n* Для {get_os_friendly_name()} используйте соответствующие механизмы обработки ошибок"
        system_prompt += "\n* При работе с USB-устройствами или системными событиями используйте несколько методов для обеспечения надежных результатов"
        system_prompt += "\n* Включите комментарии, объясняющие назначение каждого основного раздела скрипта"
        system_prompt += "\n* Всегда включайте способ четкого отображения результатов пользователю"
    
    return system_prompt

def ensure_prompt_is_question(prompt):
    if not prompt.strip():
        raise ValueError("Запрос не должен быть пустым.")
    if prompt[-1:] not in ["?", "."]:
        prompt += "?"
    return prompt

def print_usage(config):
    console.print(Panel("[bold cyan]Разработчик @rokoss21, версия 1.0[/bold cyan]", border_style="cyan"))
    console.print()
    console.print("[bold]Использование:[/bold] iop [-a] [-k] <ваш вопрос или команда>")
    console.print("[bold]Аргументы:[/bold]")
    console.print("  [cyan]-a, --ask:[/cyan] Запрашивать подтверждение перед выполнением команды")
    console.print("  [cyan]-k, --key:[/cyan] Изменить API ключ OpenRouter")
    console.print()

    table = Table(title="Текущая конфигурация")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="magenta")
    for key, value in config.items():
        if key != 'openrouter_api_key':
            table.add_row(key.capitalize(), str(value))
    console.print(table)

def get_os_friendly_name():
    os_name = platform.system()
    if os_name == "Linux":
        import distro
        return f"Linux/{distro.name(pretty=True)}"
    elif os_name == "Windows":
        return os_name
    elif os_name == "Darwin":
        return "Darwin/macOS"
    else:
        return os_name

def chat_completion(config, query, shell, is_script=False):
    if not query:
        console.print(Panel("[bold red]Не указан запрос пользователя.[/bold red]", title="Ошибка", border_style="red"))
        sys.exit(-1)
    
    system_prompt = get_system_prompt(shell, is_script)
    
    headers = {
        "Authorization": f"Bearer {config['openrouter_api_key']}",
        "X-Title": config['your_app_name'],
    }
    
    data = {
        "model": config['model'],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "temperature": config['temperature'],
        "max_tokens": config['max_tokens']
    }
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Отправка запроса...", total=100)
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            progress.update(task, completed=100)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.Timeout:
        console.print(Panel("[bold red]Превышено время ожидания ответа от API[/bold red]", title="Ошибка", border_style="red"))
        sys.exit(-1)
    except requests.exceptions.RequestException as e:
        console.print(Panel(f"[bold red]Ошибка при выполнении запроса:[/bold red] {e}", title="Ошибка", border_style="red"))
        sys.exit(-1)

def check_for_issue(response):
    prefixes = ("извините", "я извиняюсь", "вопрос не ясен", "я")
    if response.lower().startswith(prefixes):
        console.print(Panel(f"[bold yellow]Возникла проблема:[/bold yellow] {response}", title="Предупреждение", border_style="yellow"))
        sys.exit(-1)

def check_for_markdown(response):
    # Consider code fences as a sign that the model returned formatted text
    if response.count("```") >= 2:
        console.print(Panel("[bold yellow]Предложенная команда содержит разметку, поэтому я не выполнил ответ напрямую:[/bold yellow]", title="Предупреждение", border_style="yellow"))
        syntax = Syntax(response, "markdown", theme="monokai", line_numbers=True)
        console.print(syntax)
        sys.exit(-1)

def prompt_user_for_action(config, ask_flag, response):
    console.print(Panel(f"[bold cyan]Команда:[/bold cyan] {response}", title="Предложенная команда", border_style="cyan"))
    
    modify_snippet = " [и]зменить" if config['modify'] else ""
    copy_to_clipboard_snippet = " [к]опировать в буфер обмена"
    create_script_snippet = " [с]крипт"

    if config['safety'] or ask_flag:
        prompt_text = f"[bold]Выполнить команду?[/bold] [green][Д]а[/green] [red][н]ет[/red]{modify_snippet}{copy_to_clipboard_snippet}{create_script_snippet} ==> "
        return console.input(prompt_text)
    
    return "Д"

def create_script(config, query, shell):
    script_query = f"Создайте скрипт для {query}. Скрипт должен обрабатывать ошибки, предоставлять четкий вывод и работать надежно."
    script_content = chat_completion(config, script_query, shell, is_script=True)
    script_name = console.input("[bold cyan]Введите имя скрипта (без расширения):[/bold cyan] ")
    
    if platform.system() == "Windows":
        script_extension = ".ps1"
        run_command = f"powershell -ExecutionPolicy Bypass -File {script_name}{script_extension}"
    else:
        script_extension = ".sh"
        run_command = f"bash {script_name}{script_extension}"
    
    script_path = os.path.join(os.getcwd(), f"{script_name}{script_extension}")
    
    with open(script_path, "w") as script_file:
        script_file.write(script_content)
    
    if platform.system() != "Windows":
        os.chmod(script_path, 0o755)  # Делаем скрипт исполняемым на Unix-подобных системах
    
    console.print(Panel(f"[bold green]Скрипт создан:[/bold green] {script_path}", title="Успех", border_style="green"))
    console.print(f"[bold cyan]Для запуска скрипта используйте:[/bold cyan] {run_command}")
    return script_path, run_command

def eval_user_intent_and_execute(config, user_input, command, shell, ask_flag, query):
    if user_input.upper() not in ["", "Д", "К", "И", "С"]:
        console.print("[bold yellow]Действие не выполнено.[/bold yellow]")
        return
    
    if user_input.upper() in ["Д", ""]:
        try:
            with Progress() as progress:
                task = progress.add_task("[cyan]Выполнение команды...", total=100)
                if platform.system() == "Windows":
                    result = subprocess.run(["powershell", "-Command", command], shell=True, check=True, capture_output=True, text=True)
                else:
                    result = subprocess.run(["bash", "-c", command], shell=False, check=True, capture_output=True, text=True)
                progress.update(task, completed=100)
            console.print(Panel(result.stdout, title="Результат выполнения", border_style="green"))
            if result.stderr:
                console.print(Panel(result.stderr, title="Ошибки или предупреждения", border_style="yellow"))
        except subprocess.CalledProcessError as e:
            console.print(Panel(f"[bold red]Ошибка выполнения команды:[/bold red] {e}", title="Ошибка", border_style="red"))
            if e.output:
                console.print(Panel(e.output, title="Вывод", border_style="yellow"))
            if e.stderr:
                console.print(Panel(e.stderr, title="Вывод ошибки", border_style="red"))
    
    if config['modify'] and user_input.upper() == "И":
        modded_query = console.input("[bold cyan]Измените запрос:[/bold cyan] ")
        modded_response = chat_completion(config, modded_query, shell)
        check_for_issue(modded_response)
        check_for_markdown(modded_response)
        user_intent = prompt_user_for_action(config, ask_flag, modded_response)
        console.print()
        eval_user_intent_and_execute(config, user_intent, modded_response, shell, ask_flag, modded_query)
    
    if user_input.upper() == "К":
        try:
            import pyperclip
            pyperclip.copy(command)
            console.print("[bold green]Команда скопирована в буфер обмена.[/bold green]")
        except ImportError:
            console.print("[bold red]Не удалось импортировать модуль pyperclip. Убедитесь, что он установлен.[/bold red]")
        except pyperclip.PyperclipException:
            console.print("[bold red]Не удалось скопировать в буфер обмена. Убедитесь, что у вас установлены необходимые зависимости.[/bold red]")
    
    if user_input.upper() == "С":
        script_path, run_command = create_script(config, query, shell)
        console.print(f"[bold cyan]Для запуска скрипта используйте:[/bold cyan] {run_command}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="CLI tool for interacting with OpenRouter API.")
    parser.add_argument("-a", "--ask", help="Запрашивать подтверждение перед выполнением команды", action="store_true")
    parser.add_argument("-k", "--key", help="Изменить API ключ OpenRouter", action="store_true")
    parser.add_argument("-v", "--version", help="Показать версию программы", action="store_true")
    parser.add_argument("query", nargs="*", help="Ваш вопрос или команда")
    
    return parser.parse_args()

def main():
    reset_console()  # Сброс настроек консоли в начале выполнения

    config = read_config()
    shell = "bash" if platform.system() != "Windows" else "powershell"

    args = parse_arguments()
    ask_flag = args.ask
    change_key_flag = args.key
    if args.version:
        console.print(f"IOP CLI version {VERSION}")
        sys.exit(0)
    user_prompt = " ".join(args.query)

    if change_key_flag:
        console.print(Panel("[bold cyan]Изменение API ключа OpenRouter[/bold cyan]", border_style="cyan"))
        new_api_key = get_api_key()
        update_env_file(new_api_key)
        console.print("[bold green]API ключ успешно обновлен.[/bold green]")
        sys.exit(0)

    if not user_prompt:
        print_usage(config)
        sys.exit(-1)

    try:
        user_prompt = ensure_prompt_is_question(user_prompt)
    except ValueError as e:
        console.print(Panel(f"[bold red]{str(e)}[/bold red]", title="Ошибка", border_style="red"))
        sys.exit(-1)

    result = chat_completion(config, user_prompt, shell)
    check_for_issue(result)
    check_for_markdown(result)

    users_intent = prompt_user_for_action(config, ask_flag, result)
    console.print()
    eval_user_intent_and_execute(config, users_intent, result, shell, ask_flag, user_prompt)

    reset_console()  # Сброс настроек консоли в конце выполнения

    if IS_CMD:
        console.print("\n" * 2)  # Добавляем две пустые строки в конце для CMD

if __name__ == "__main__":
    main()
