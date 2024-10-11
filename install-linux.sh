#!/bin/bash

set -e

echo "===== Установка IOP для Linux ====="

# Проверка наличия необходимых файлов
if [ ! -f "iop.py" ]; then
    echo "Ошибка: Файл iop.py не найден в текущей директории."
    echo "Убедитесь, что вы запускаете этот скрипт из правильной директории."
    exit 1
fi

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Python не установлен. Пожалуйста, установите Python 3.7 или выше."
    echo "Вы можете установить Python, используя менеджер пакетов вашего дистрибутива."
    echo "Например, для Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "После установки Python запустите этот скрипт снова."
    exit 1
fi

# Проверка наличия pip и venv
if ! python3 -m pip --version &> /dev/null; then
    echo "pip не установлен. Установите его с помощью менеджера пакетов вашего дистрибутива."
    echo "Например, для Ubuntu/Debian: sudo apt-get install python3-pip"
    exit 1
fi

if ! python3 -m venv --help &> /dev/null; then
    echo "venv не установлен. Установите его с помощью менеджера пакетов вашего дистрибутива."
    echo "Например, для Ubuntu/Debian: sudo apt-get install python3-venv"
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

# Создание символической ссылки
install_dir=""
if [ -w "/usr/local/bin" ]; then
    install_dir="/usr/local/bin"
elif [ -w "$HOME/.local/bin" ]; then
    install_dir="$HOME/.local/bin"
else
    mkdir -p "$HOME/.local/bin"
    install_dir="$HOME/.local/bin"
fi

ln -sf "$(pwd)/iop" "$install_dir/iop"

echo
echo "Установка завершена успешно!"
echo "Теперь вы можете использовать команду 'iop [запрос]' в любом месте системы."
echo "Если возникли проблемы, убедитесь, что $install_dir находится в вашем PATH."
echo "Вы можете добавить его, выполнив команду: export PATH=\$PATH:$install_dir"
echo "Добавьте эту команду в ваш ~/.bashrc или ~/.zshrc файл для постоянного эффекта."

# Проверка наличия директории в PATH
if [[ ":$PATH:" != *":$install_dir:"* ]]; then
    echo "ВНИМАНИЕ: $install_dir не находится в вашем PATH."
    echo "Добавьте следующую строку в ваш ~/.bashrc или ~/.zshrc файл:"
    echo "export PATH=\$PATH:$install_dir"
fi
