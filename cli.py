import platform
import sys

import utils
import openrouter
import prompt as prompt_module
import executor

VERSION = "1.01"


# ----------------------------------------------------------------------------
# Argument parsing
# ----------------------------------------------------------------------------

import argparse

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CLI tool for interacting with OpenRouter API.")
    parser.add_argument("query", nargs="*", help="Ваш вопрос или команда")
    parser.add_argument("-a", "--ask", action="store_true", help="Запрашивать подтверждение перед выполнением команды")
    parser.add_argument("-k", "--key", action="store_true", help="Изменить API ключ OpenRouter")
    parser.add_argument("-v", "--version", action="store_true", help="Показать версию программы")
    return parser.parse_args()


# ----------------------------------------------------------------------------
# Main routine
# ----------------------------------------------------------------------------

def main() -> None:
    utils.reset_console()

    config = openrouter.read_config()
    shell = "bash" if platform.system() != "Windows" else "powershell"

    args = parse_arguments()

    if args.version:
        utils.console.print(f"IOP CLI version {VERSION}")
        sys.exit(0)

    if args.key:
        utils.console.print("[bold cyan]Изменение API ключа OpenRouter[/bold cyan]", markup=True)
        new_api_key = openrouter.get_api_key()
        openrouter.update_env_file(new_api_key)
        utils.console.print("[bold green]API ключ успешно обновлен.[/bold green]", markup=True)
        sys.exit(0)

    user_prompt: str = " ".join(args.query)
    if not user_prompt:
        prompt_module.print_usage(config)
        sys.exit(-1)

    try:
        user_prompt = prompt_module.ensure_prompt_is_question(user_prompt)
    except ValueError as exc:
        utils.console.print(f"[bold red]{str(exc)}[/bold red]", markup=True)
        sys.exit(-1)

    result = openrouter.chat_completion(config, user_prompt, shell)
    executor.check_for_issue(result)
    executor.check_for_markdown(result)

    user_intent = executor.prompt_user_for_action(config, args.ask, result)
    utils.console.print()
    executor.eval_user_intent_and_execute(config, user_intent, result, shell, args.ask, user_prompt)

    utils.reset_console()

    if utils.IS_CMD:
        utils.console.print("\n" * 2)


if __name__ == "__main__":
    main()