# IOP CLI 1.01 🚀

## Содержание
1. [Описание](#описание)
2. [Возможности](#возможности)
3. [Требования](#требования)
4. [Установка](#установка)
5. [Настройка](#настройка)
6. [Использование](#использование)
7. [Примеры](#примеры)
8. [Создание скриптов](#создание-скриптов)
9. [Устранение неполадок](#устранение-неполадок)
10. [Конфигурация по умолчанию](#конфигурация-по-умолчанию)
11. [Вклад в проект](#вклад-в-проект)
12. [Лицензия](#лицензия)
13. [Контакты](#контакты)

## Описание

IOP CLI (Intelligent Operations Command Line Interface) - это мощный инструмент командной строки, использующий OpenRouter API для выполнения различных задач с помощью искусственного интеллекта. IOP позволяет пользователям взаимодействовать с AI-моделями через простой интерфейс командной строки, получая помощь в решении широкого спектра задач - от анализа данных до генерации кода.

## Возможности

- 🌈 **Кросс-платформенность**: Работает на Linux, macOS и Windows
- 🔧 **Гибкая настройка**: Легко конфигурируется через YAML файл
- 🔐 **Безопасность**: Поддерживает режим подтверждения команд
- 🎨 **Улучшенный вывод**: Цветное форматирование для удобства чтения
- 📋 **Интеграция с буфером обмена**: Быстрое сохранение результатов
- 🔄 **Поддержка различных моделей**: Возможность выбора любой модели из OpenRouter
- 🛠 **Выполнение команд**: Автоматическое выполнение сгенерированных команд (с подтверждением)
- 🔑 **Управление API ключом**: Автоматический запрос и валидация API ключа при первом запуске, возможность изменения ключа
- 🐍 **Улучшенное обнаружение Python**: Автоматический поиск Python в стандартных местах установки
- 🌐 **Виртуальное окружение**: Автоматическое создание и использование виртуального окружения для изоляции зависимостей
- 📜 **Создание скриптов**: Возможность создания полноценных скриптов на основе запросов пользователя
- 🌍 **Многоязычный интерфейс**: Поддержка русского языка в интерфейсе и сообщениях
- 📝 **Улучшенное логирование**: Подробное логирование для облегчения отладки
- 🔄 **Обработка аргументов командной строки**: Гибкая настройка параметров запуска
- ⚠️ **Улучшенная обработка ошибок**: Более информативные сообщения об ошибках и их обработка
- 🎭 **Стильный интерфейс**: Использование библиотеки `rich` для создания современного и удобного интерфейса (новое в версии 1.01)
- 📊 **Прогресс-бары**: Визуализация процессов выполнения команд (новое в версии 1.01)
- 📦 **Структурированный вывод**: Использование панелей и таблиц для лучшей организации информации (новое в версии 1.01)
- 🌈 **Расширенное цветовое оформление**: Улучшенная цветовая схема для различных типов сообщений (новое в версии 1.01)

## Требования

- Python 3.7+
- Доступ к интернету для взаимодействия с OpenRouter API
- Библиотека `rich` (новое в версии 1.01)

## Установка

Теперь установка IOP стала еще проще благодаря новым установочным скриптам:

### Windows:
1. Скачайте файлы IOP в одну директорию.
2. Запустите `install-win.bat` от имени администратора.
3. Следуйте инструкциям на экране.

### Linux:
1. Скачайте файлы IOP в одну директорию.
2. Откройте терминал в этой директории.
3. Выполните:
   ```
   chmod +x install-linux.sh
   ./install-linux.sh
   ```

### macOS:
1. Скачайте файлы IOP в одну директорию.
2. Откройте терминал в этой директории.
3. Выполните:
   ```
   chmod +x install-mac.sh
   ./install-mac.sh
   ```

Установочные скрипты автоматически:
- Проверяют наличие Python и устанавливают его, если необходимо
- Создают виртуальное окружение
- Устанавливают все необходимые зависимости, включая `rich` (новое в версии 1.01)
- Настраивают IOP для работы из любой директории

## Настройка

Отредактируйте файл `config.yaml` для настройки параметров:

```yaml
api: openrouter
your_app_name: "IOP CLI"
model: openai/gpt-4o-mini  # Можно изменить на любую модель OpenRouter
temperature: 0.7
max_tokens: 500
safety: true
modify: true
suggested_command_color: cyan
user_message_color: green
assistant_message_color: blue
error_message_color: red
```

## Использование

Базовое использование:
```
iop <ваш запрос>
```

С запросом подтверждения перед выполнением команды:
```
iop -a <ваш запрос>
```
или
```
iop --ask <ваш запрос>
```

Изменение API ключа:
```
iop -k
```
или
```
iop --key
```

Получение справки:
```
iop -h
```
или
```
iop --help
```

## Примеры

1. **Получение информации о системе**:
   ```
   iop какая у меня операционная система?
   ```

2. **Создание файла**:
   ```
   iop создай текстовый файл с именем example.txt и содержанием "Hello, World!"
   ```

3. **Анализ данных**:
   ```
   iop проанализируй файл log.txt и найди все ошибки
   ```

4. **Генерация кода**:
   ```
   iop напиши простой Python скрипт для веб-скрапинга
   ```

5. **Выполнение системных операций**:
   ```
   iop -a очисти кэш браузера Chrome
   ```

## Создание скриптов

IOP теперь может создавать полноценные скрипты на основе ваших запросов:

1. Используйте команду с опцией [с]крипт:
   ```
   iop создай скрипт для резервного копирования важных файлов
   ```

2. Выберите опцию [с]крипт при выполнении команды.

3. Введите имя для скрипта, когда будет предложено.

4. IOP создаст скрипт, учитывающий особенности вашей операционной системы и включающий обработку ошибок.

## Устранение неполадок

Если у вас возникли проблемы:

1. **Проверьте установку Python**:
   - Убедитесь, что Python версии 3.7 или выше установлен и доступен в системном PATH.
   - Если Python не обнаружен, установочный скрипт предложит инструкции по установке.

2. **Проверьте API ключ**:
   - Убедитесь, что вы ввели правильный API ключ OpenRouter.
   - Если ключ неверный, используйте команду `iop -k` для его изменения.

3. **Проверьте виртуальное окружение**:
   - Убедитесь, что виртуальное окружение создано и активировано.
   - Если возникли проблемы, попробуйте удалить директорию `iop-env` и запустить установочный скрипт заново.

4. **Проверьте права доступа**:
   - Убедитесь, что у вас есть права на выполнение скриптов и доступ к необходимым директориям.

5. **Проверьте подключение к интернету**:
   - IOP требует стабильного подключения к интернету для работы с OpenRouter API.

6. **Проверьте логи**:
   - IOP теперь ведет подробное логирование. Проверьте файл лога для получения дополнительной информации об ошибках.

7. **Проверьте установку библиотеки `rich`** (новое в версии 1.01):
   - Убедитесь, что библиотека `rich` установлена корректно. Если нет, попробуйте переустановить ее вручную:
     ```
     pip install rich
     ```

Если проблемы сохраняются, пожалуйста, создайте issue в репозитории проекта с подробным описанием проблемы, информацией о вашей системе и содержимым лог-файла.

## Конфигурация по умолчанию

Если файл конфигурации отсутствует или некоторые параметры не указаны, IOP использует следующие значения по умолчанию:

```python
config = {
    'model': 'gpt-4',
    'temperature': 0.7,
    'max_tokens': 1500,
    'your_app_name': 'CLI Tool',
    'error_message_color': 'red',
    'user_message_color': 'blue',
    'assistant_message_color': 'green',
    'suggested_command_color': 'yellow',
    'modify': True,
    'safety': True
}
```

Вы можете переопределить эти значения в вашем `config.yaml` файле.

## Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста, следуйте этим шагам:

1. Форкните репозиторий
2. Создайте ветку для вашей функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте ваши изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте изменения в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## Лицензия

Распространяется под лицензией MIT. Смотрите `LICENSE` для получения дополнительной информации.

## Контакты

Разработчик - [@rokoss21](https://github.com/rokoss21)

Ссылка на проект: (https://github.com/rokoss21/iop)

---

Мы надеемся, что IOP CLI станет вашим надежным помощником в повседневных задачах и сложных проектах. Не стесняйтесь обращаться с вопросами, предложениями или сообщениями об ошибках. Удачи в использовании IOP CLI!

## Что нового в версии 1.01

- 🎭 **Стильный интерфейс**: Внедрение библиотеки `rich` для создания современного и удобного интерфейса командной строки.
- 📊 **Прогресс-бары**: Добавлены визуальные индикаторы прогресса для длительных операций.
- 📦 **Структурированный вывод**: Использование панелей и таблиц для лучшей организации и представления информации.
- 🌈 **Расширенное цветовое оформление**: Улучшенная цветовая схема для различных типов сообщений, повышающая читаемость и удобство использования.
- 🔧 **Оптимизация кода**: Рефакторинг для улучшения производительности и читаемости кода.
- 📚 **Обновленная документация**: Расширенное описание новых функций и возможностей в README.

Эти улучшения делают IOP CLI еще более мощным и удобным инструментом для выполнения разнообразных задач с помощью искусственного интеллекта.
