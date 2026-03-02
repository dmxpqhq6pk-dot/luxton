# Инструкция по деплою на PythonAnywhere

## Шаг 1: Регистрация
1. Зайди на https://www.pythonanywhere.com
2. Зарегистрируйся (Beginner account - бесплатный)

## Шаг 2: Открой Bash консоль
1. После входа нажми "Consoles" в меню
2. Выбери "Bash"

## Шаг 3: Клонируй репозиторий
```bash
git clone https://github.com/dmxpqhq6pk-dot/luxton.git
cd luxton
```

## Шаг 4: Установи зависимости
```bash
pip3 install --user -r requirements.txt
```

## Шаг 5: Настрой переменные окружения
```bash
echo 'export BOT_TOKEN="7205371569:AAGM4zv59yX3-9Z9MJhMY9T7Vzwdc6iutMQ"' >> ~/.bashrc
echo 'export SUPPORT_CHAT_ID="-1002831062931"' >> ~/.bashrc
echo 'export SUPPORT_ACCOUNT_ID="8222462689"' >> ~/.bashrc
source ~/.bashrc
```

## Шаг 6: Создай Always-On Task
1. Перейди в раздел "Tasks" в меню
2. Нажми "Create a new scheduled task"
3. В поле "Command" введи:
```
/home/ТВОЙ_USERNAME/luxton/bot.py
```
4. Установи время запуска (например, каждый день в 00:00)
5. Нажми "Create"

## Шаг 7: Запусти бота вручную первый раз
```bash
cd ~/luxton
python3 bot.py
```

## Важно!
- Бесплатный аккаунт требует перезапуска каждые 3 месяца
- Бот будет работать постоянно, пока не истечет срок
- Можно настроить автоматический перезапуск через scheduled tasks

## Проверка работы
Отправь `/start` боту в Telegram - он должен ответить!
