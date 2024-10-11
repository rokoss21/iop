#!/bin/bash

set -e

echo "===== Установка IOP для macOS ====="

# Проверка наличия необходимых файлов
if [ ! -f "iop.py" ]; then
    echo "Ошибка: Файл iop.py не найден в текущей директории."
    echo "Убедитесь, что вы запускаете этот скрипт из правильной директории."
    exit 1
fi

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Python не установлен. Пожалуйста, установите Python 3.7 или выше."
    echo "Вы можете установить Python, используя Homebrew: brew install python"
    echo "Или скачайте с официального сайта: https://www.python.org/downloads/"
    echo "После установки Python запустите этот скрипт снова."
    exit 1
fi

# Проверка наличия pip и venv
if ! python3 -m pip --version &> /dev/null; then
    echo "pip не установлен. Установите его с помощью команды:"
    echo "python3 -m ensurepip --upgrade"
    exit 1
fi

if ! python3 -m venv --help &> /dev/null; then
    echo "venv не установлен. Он должен быть частью стандартной установки Python."
    echo "Попробуйте переустановить Python."
    exit 1
fi

# Создание виртуального окружения
echo "Создание виртуального окружения..."
python3 -m venv iop-env

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source iop-env/bin/activate

# Установка зависимостей
echo "Установка зависимостей..."
pip install requests pyyaml python-dotenv termcolor colorama pyperclip

# Создание bash-скрипта для запуска IOP
echo "#!/bin/bash" > iop
echo "source \"$(pwd)/iop-env/bin/activate\"" >> iop
echo "python \"$(pwd)/iop.py\" \"\$@\"" >> iop
echo "deactivate" >> iop

# Установка прав на выполнение
chmod +x iop

# Определение директории для установки
if [ -d "/opt/homebrew/bin" ]; then
    # macOS с Apple Silicon
    install_dir="/opt/homebrew/bin"
elif [ -w "/usr/local/bin" ]; then
    # Стандартная директория для Intel Mac
    install_dir="/usr/local/bin"
else
    # Установка в пользовательскую директорию, если нет прав на запись в системные директории
    install_dir="$HOME/.local/bin"
    mkdir -p "$install_dir"
fi

# Создание символической ссылки
ln -sf "$(pwd)/iop" "$install_dir/iop"

echo
echo "Установка завершена успешно!"
echo "Теперь вы можете использовать команду 'iop [запрос]' в любом месте системы."
echo "Если возникли проблемы, убедитесь, что $install_dir находится в вашем PATH."

# Проверка наличия директории в PATH
if [[ ":$PATH:" != *":$install_dir:"* ]]; then
    echo "ВНИМАНИЕ: $install_dir не находится в вашем PATH."
    echo "Добавьте следующую строку в ваш ~/.bash_profile или ~/.zshrc файл:"
    echo "export PATH=\$PATH:$install_dir"
fi

echo "Для применения изменений перезапустите терминал или выполните команду: source ~/.bash_profile (или ~/.zshrc)"
