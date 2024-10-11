@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ===== Установка IOP для Windows =====

REM Проверка наличия необходимых файлов
if not exist "iop.py" (
    echo Ошибка: Файл iop.py не найден в текущей директории.
    echo Убедитесь, что вы запускаете этот скрипт из правильной директории.
    pause
    exit /b 1
)

REM Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден. Проверяем альтернативные пути...
    
    REM Проверка стандартных путей установки Python
    set "python_paths=C:\Python39;C:\Python38;C:\Python37;%LOCALAPPDATA%\Programs\Python\Python39;%LOCALAPPDATA%\Programs\Python\Python38;%LOCALAPPDATA%\Programs\Python\Python37"
    
    for %%p in (%python_paths%) do (
        if exist "%%p\python.exe" (
            set "PYTHON_PATH=%%p"
            goto :python_found
        )
    )
    
    echo Python не найден в стандартных местах установки.
    goto :python_not_found
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set python_version=%%i
    echo Найдена версия Python: !python_version!
    set "PYTHON_PATH=python"
    goto :python_found
)

:python_not_found
echo.
echo Не удалось найти подходящую версию Python (3.7 или выше).
echo Если Python установлен, убедитесь, что он добавлен в системный PATH.
echo.
echo Чтобы добавить Python в PATH:
echo 1. Откройте "Параметры системы"
echo 2. Перейдите в "Дополнительные параметры системы"
echo 3. Нажмите "Переменные среды"
echo 4. В разделе "Системные переменные" найдите и выберите "Path"
echo 5. Нажмите "Изменить" и добавьте путь к директории Python и Python\Scripts
echo.
echo Если Python не установлен, скачайте его с https://www.python.org/downloads/
echo После установки Python или обновления PATH, запустите этот скрипт снова.
pause
exit /b 1

:python_found
echo Python успешно обнаружен.

REM Создание виртуального окружения
echo Создание виртуального окружения...
%PYTHON_PATH% -m venv iop-env
if %errorlevel% neq 0 (
    echo Не удалось создать виртуальное окружение. Проверьте права доступа и попробуйте снова.
    pause
    exit /b 1
)

REM Активация виртуального окружения
echo Активация виртуального окружения...
call iop-env\Scripts\activate.bat

REM Установка зависимостей
echo Установка зависимостей...
python -m pip install --upgrade pip
pip install requests pyyaml python-dotenv termcolor colorama pyperclip
if %errorlevel% neq 0 (
    echo Не удалось установить зависимости. Проверьте подключение к интернету и попробуйте снова.
    pause
    exit /b 1
)

REM Создание bat-файла для запуска IOP
echo @echo off > iop.bat
echo chcp 65001 ^> nul >> iop.bat
echo call "%cd%\iop-env\Scripts\activate.bat" >> iop.bat
echo python "%cd%\iop.py" %%* >> iop.bat
echo deactivate >> iop.bat

REM Добавление пути к iop.bat в PATH
set "folder_path=%cd%"
set "path_to_add=!folder_path!"
setx PATH "%PATH%;!path_to_add!"
if %errorlevel% neq 0 (
    echo Не удалось добавить путь в PATH. Вы можете сделать это вручную, добавив следующий путь в переменную среды PATH:
    echo !path_to_add!
) else (
    echo Путь успешно добавлен в PATH.
)

echo.
echo Установка завершена успешно!
echo Теперь вы можете использовать команду 'iop [запрос]' в любом месте системы.
echo Если команда 'iop' не работает, перезапустите командную строку или компьютер.
pause
