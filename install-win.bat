@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Запрос прав администратора
NET SESSION >nul 2>&1
if %errorlevel% neq 0 (
    echo Запуск от имени администратора...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

:: Проверка наличия Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python не найден в PATH. Попытка автоматического обнаружения...
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_PATH=%%i"
            goto :python_found
        )
    )
    echo Python не найден. Пожалуйста, установите Python и добавьте его в PATH.
    echo Вы можете скачать Python с https://www.python.org/downloads/
    echo При установке убедитесь, что отмечена опция "Add Python to PATH"
    pause
    exit /b 1
)

:python_found
if defined PYTHON_PATH (
    echo Python найден: !PYTHON_PATH!
    echo Добавление Python в PATH...
    setx PATH "%PATH%;!PYTHON_PATH!;!PYTHON_PATH!\Scripts" /M
    set "PATH=%PATH%;!PYTHON_PATH!;!PYTHON_PATH!\Scripts"
) else (
    echo Python уже находится в PATH.
)

:: Проверка версии Python
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Обнаружена версия Python: %PYTHON_VERSION%

:: Проверка наличия необходимых файлов
if not exist "%~dp0iop.py" ( echo iop.py отсутствует в %~dp0, установка невозможна & goto :end )
if not exist "%~dp0prompt.txt" ( echo prompt.txt отсутствует в %~dp0, установка невозможна & goto :end )
if not exist "%~dp0config.yaml" ( echo config.yaml отсутствует в %~dp0, установка невозможна & goto :end )
if not exist "%~dp0ai_model.py" ( echo ai_model.py отсутствует в %~dp0, установка невозможна & goto :end )

:: Установка значений по умолчанию
set "INSTALL_DIR=%USERPROFILE%\iop-cli"

:menu
cls
echo Установщик IOP
echo ---------------
echo [1] Установка по умолчанию (в %USERPROFILE%\iop-cli)
echo [2] Выбрать другую директорию для установки
echo [3] Выход
choice /C 123 /N /M "Выберите опцию (1-3): "
if errorlevel 3 goto :end
if errorlevel 2 goto :custom_install
if errorlevel 1 goto :install

:custom_install
cls
echo Пользовательская установка
echo ---------------------------
set /p INSTALL_DIR="Введите путь для установки IOP (по умолчанию %USERPROFILE%\iop-cli): "
if "!INSTALL_DIR!"=="" set "INSTALL_DIR=%USERPROFILE%\iop-cli"

:install
if not exist "!INSTALL_DIR!" mkdir "!INSTALL_DIR!"

echo Копирование файлов...
copy "%~dp0iop.py" "!INSTALL_DIR!"
copy "%~dp0prompt.txt" "!INSTALL_DIR!"
copy "%~dp0config.yaml" "!INSTALL_DIR!"
copy "%~dp0ai_model.py" "!INSTALL_DIR!"

echo Создание виртуального окружения...
python -m venv "!INSTALL_DIR!\iop-env"
if %errorlevel% neq 0 (
    echo Ошибка при создании виртуального окружения.
    goto :end
)

echo Создание iop.bat...
(
echo @echo off
echo chcp 65001 ^>nul
echo call "!INSTALL_DIR!\iop-env\Scripts\activate.bat"
echo python "!INSTALL_DIR!\iop.py" %%*
echo call "!INSTALL_DIR!\iop-env\Scripts\deactivate.bat"
) > "!INSTALL_DIR!\iop.bat"

echo Установка зависимостей...
call "!INSTALL_DIR!\iop-env\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install PyYAML==6.0.1 requests==2.26.0 python-dotenv==0.19.1 pyperclip termcolor==1.1.0 colorama==0.4.4 distro==1.6.0
if %errorlevel% neq 0 (
    echo Ошибка при установке зависимостей.
    goto :end
)

:: Добавление директории в PATH
echo Добавление директории в PATH...
set "PATH_TO_ADD=!INSTALL_DIR!"
setx PATH "%PATH%;%PATH_TO_ADD%" /M
if %errorlevel% neq 0 (
    echo Не удалось добавить директорию в PATH. Пожалуйста, добавьте !INSTALL_DIR! в PATH вручную.
) else (
    echo Директория успешно добавлена в PATH.
    :: Обновление PATH для текущей сессии
    set "PATH=%PATH%;%PATH_TO_ADD%"
)

:: Создание символической ссылки для глобального доступа
echo Создание символической ссылки для глобального доступа...
if exist "%SystemRoot%\iop.bat" (
    echo Символическая ссылка уже существует.
) else (
    mklink "%SystemRoot%\iop.bat" "!INSTALL_DIR!\iop.bat"
    if %errorlevel% neq 0 (
        echo Не удалось создать символическую ссылку. Убедитесь, что вы запустили скрипт от имени администратора.
    ) else (
        echo Символическая ссылка успешно создана.
    )
)

echo.
echo Установка завершена!
echo IOP установлен в: !INSTALL_DIR!
echo.
echo Теперь вы можете использовать команду 'iop [ваш запрос]' из любого места в системе.
echo Если команда не работает, попробуйте перезапустить командную строку или PowerShell.

:end
pause
