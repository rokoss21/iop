#!/usr/bin/env python3

import os
import platform
import sys
import subprocess
import dotenv 
import distro
import yaml
import pyperclip
import requests
from termcolor import colored
from colorama import init

def validate_api_key(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    try:
        response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_api_key():
    while True:
        api_key = input("Введите ваш API ключ OpenRouter: ")
        if validate_api_key(api_key):
            return api_key
        print(colored("Неверный API ключ. Пожалуйста, попробуйте снова.", 'red'))

def update_env_file(api_key):
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    with open(env_path, "w") as env_file:
        env_file.write(f"OPENROUTER_API_KEY={api_key}")
    os.chmod(env_path, 0o600)  # Устанавливаем права доступа только для владельца

def read_config():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        print(colored("Файл .env не найден. Пожалуйста, введите API ключ OpenRouter.", 'yellow'))
        api_key = get_api_key()
        update_env_file(api_key)
    else:
        dotenv.load_dotenv(env_path)
    
    config['openrouter_api_key'] = os.getenv('OPENROUTER_API_KEY')
    
    if not config['openrouter_api_key']:
        print(colored("API ключ OpenRouter не найден. Пожалуйста, введите его.", 'yellow'))
        api_key = get_api_key()
        update_env_file(api_key)
        config['openrouter_api_key'] = api_key
    
    return config

def get_system_prompt(shell, is_script=False):
    prompt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.txt")
    with open(prompt_file, "r") as file:
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
    if prompt[-1:] not in ["?", "."]:
        prompt += "?"
    return prompt

def print_usage(config):
    print(colored("Разработчик @rokoss21, версия 1.0", 'cyan'))
    print()
    print(colored("Использование: iop [-a] [-k] <ваш вопрос или команда>", 'yellow'))
    print(colored("Аргументы:", 'yellow'))
    print(colored("  -a: Запрашивать подтверждение перед выполнением команды (полезно только когда безопасность отключена)", 'yellow'))
    print(colored("  -k: Изменить API ключ OpenRouter", 'yellow'))
    print()

    print(colored("Текущая конфигурация:", 'cyan'))
    for key, value in config.items():
        if key != 'openrouter_api_key':
            print(colored(f"* {key.capitalize():13}: {value}", 'cyan'))

def get_os_friendly_name():
    os_name = platform.system()
    if os_name == "Linux":
        return f"Linux/{distro.name(pretty=True)}"
    elif os_name == "Windows":
        return os_name
    elif os_name == "Darwin":
        return "Darwin/macOS"
    else:
        return os_name

def chat_completion(config, query, shell, is_script=False):
    if not query:
        print(colored("Не указан запрос пользователя.", config['error_message_color']))
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
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(colored(f"Ошибка: {e}", config['error_message_color']))
        sys.exit(-1)

def check_for_issue(response, config):
    prefixes = ("извините", "я извиняюсь", "вопрос не ясен", "я")
    if response.lower().startswith(prefixes):
        print(colored(f"Возникла проблема: {response}", config['error_message_color']))
        sys.exit(-1)

def check_for_markdown(response, config):
    if response.count("```", 2):
        print(colored("Предложенная команда содержит разметку, поэтому я не выполнил ответ напрямую:", config['error_message_color']))
        print(response)
        sys.exit(-1)

def prompt_user_for_action(config, ask_flag, response):
    print(colored("Команда: ", config['user_message_color']) + colored(response, config['suggested_command_color'], attrs=['bold']))
    
    modify_snippet = " [и]зменить" if config['modify'] else ""
    copy_to_clipboard_snippet = " [к]опировать в буфер обмена"
    create_script_snippet = " [с]крипт"

    if config['safety'] or ask_flag:
        prompt_text = f"Выполнить команду? [Д]а [н]ет{modify_snippet}{copy_to_clipboard_snippet}{create_script_snippet} ==> "
        return input(colored(prompt_text, config['user_message_color']))
    
    return "Д"

def create_script(config, query, shell):
    script_query = f"Создайте скрипт для {query}. Скрипт должен обрабатывать ошибки, предоставлять четкий вывод и работать надежно."
    script_content = chat_completion(config, script_query, shell, is_script=True)
    script_name = input(colored("Введите имя скрипта (без расширения): ", config['user_message_color']))
    
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
    
    print(colored(f"Скрипт создан: {script_path}", config['assistant_message_color']))
    print(colored(f"Для запуска скрипта используйте: {run_command}", config['assistant_message_color']))
    return script_path, run_command

def eval_user_intent_and_execute(config, user_input, command, shell, ask_flag, query):
    if user_input.upper() not in ["", "Д", "К", "И", "С"]:
        print(colored("Действие не выполнено.", config['assistant_message_color']))
        return
    
    if user_input.upper() in ["Д", ""]:
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["powershell", "-Command", command], shell=True, check=True, capture_output=True, text=True)
            else:
                result = subprocess.run(["bash", "-c", command], shell=False, check=True, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(colored(f"Ошибки или предупреждения:\n{result.stderr}", config['error_message_color']))
        except subprocess.CalledProcessError as e:
            print(colored(f"Ошибка выполнения команды: {e}", config['error_message_color']))
            if e.output:
                print(colored(f"Вывод:\n{e.output}", config['error_message_color']))
            if e.stderr:
                print(colored(f"Вывод ошибки:\n{e.stderr}", config['error_message_color']))
    
    if config['modify'] and user_input.upper() == "И":
        modded_query = input(colored("Измените запрос: ", config['user_message_color']))
        modded_response = chat_completion(config, modded_query, shell)
        check_for_issue(modded_response, config)
        check_for_markdown(modded_response, config)
        user_intent = prompt_user_for_action(config, ask_flag, modded_response)
        print()
        eval_user_intent_and_execute(config, user_intent, modded_response, shell, ask_flag, modded_query)
    
    if user_input.upper() == "К":
        try:
            pyperclip.copy(command)
            print(colored("Команда скопирована в буфер обмена.", config['assistant_message_color']))
        except pyperclip.PyperclipException:
            print(colored("Не удалось скопировать в буфер обмена. Убедитесь, что у вас установлены необходимые зависимости.", config['error_message_color']))
    
    if user_input.upper() == "С":
        script_path, run_command = create_script(config, query, shell)
        print(colored(f"Для запуска скрипта используйте: {run_command}", config['assistant_message_color']))

def main():
    init()  # Включаем цветной вывод на Windows с помощью colorama

    config = read_config()
    
    shell = "bash" if platform.system() != "Windows" else "powershell"

    command_start_idx = 1
    ask_flag = False
    change_key_flag = False

    if len(sys.argv) < 2:
        print_usage(config)
        sys.exit(-1)

    if "-a" in sys.argv:
        ask_flag = True
        sys.argv.remove("-a")

    if "-k" in sys.argv:
        change_key_flag = True
        sys.argv.remove("-k")

    if change_key_flag:
        print(colored("Изменение API ключа OpenRouter", 'yellow'))
        new_api_key = get_api_key()
        update_env_file(new_api_key)
        print(colored("API ключ успешно обновлен.", 'green'))
        sys.exit(0)

    user_prompt = " ".join(sys.argv[command_start_idx:])

    result = chat_completion(config, user_prompt, shell) 
    check_for_issue(result, config)
    check_for_markdown(result, config)

    users_intent = prompt_user_for_action(config, ask_flag, result)
    print()
    eval_user_intent_and_execute(config, users_intent, result, shell, ask_flag, user_prompt)

if __name__ == "__main__":
    main()
