# Telegramm-Sport-Bot

Telegram-бот для расчёта КБЖУ и подбора продуктов под дневной бюджет, а также парсер товаров для наполнения базы.

Репозиторий содержит две ветки:

- `main` — бот, мониторинг и деплой на сервер.
- `parser` — парсер товаров, база PostgreSQL и Redis. Отдельного CI/CD-воркфлоу не имеет.

## Бот (ветка `main`)

Поддерживает три метода расчёта калорий:
- Формула Харриса-Бенедикта
- Формула Миффлина-Сан Жеора
- Ручной ввод известных калорий

После расчёта пользователь вводит дневной бюджет, и бот формирует список продуктов (основное блюдо / гарнир / напиток) из PostgreSQL-базы.

### Технологии

- Python 3.11, pyTelegramBotAPI
- PostgreSQL
- Docker, Docker Compose
- Prometheus, Alertmanager, Grafana, Node Exporter (мониторинг)
- GitHub Actions (тест, сборка образа, деплой на сервер)

### Структура

- `TgBot/` — код бота
- `prometheus/`, `alertmanager/` — конфигурация мониторинга
- `docker-compose.yml` — запуск бота и мониторинга
- `.github/workflows/pipeline.yml` — CI/CD

### Переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cp .env.example .env
```

Переменная	Описание
API	Токен Telegram-бота (получить у @BotFather)
DATABASE_URL	URL подключения к PostgreSQL
ALERTMANAGER_BOT_TOKEN	Токен отдельного бота для алертов
ALERTMANAGER_CHAT_ID	ID чата для получения алертов
GF_SECURITY_ADMIN_USER	Логин администратора Grafana
GF_SECURITY_ADMIN_PASSWORD	Пароль администратора Grafana

Локальный запуск

```bash
docker compose up -d
```

##CI/CD

При пуше в ветку main:

    Test: установка зависимостей из requirements.txt.
    Build: сборка Docker-образа и пуш в Docker Hub.
    Deploy: SSH-деплой на сервер, docker compose pull && docker compose up -d.

Для деплоя в настройках репозитория (Settings → Secrets and variables → Actions) должны быть заданы секреты DOCKER_USERNAME, DOCKER_PASSWORD, HOST_IP, HOST_USER, HOST_PASSWD.

##Парсер (ветка 'parser')

Парсер собирает товары ВкусВилл через MCP-сервер ВкусВилл и сохраняет их в PostgreSQL. Бот читает эту базу при подборе продуктов.
Состав

parser/mcp_client.py — клиент MCP-сервера ВкусВилл (поиск товаров, детали, штрихкоды, аналоги, акции, магазины, рецепты). Делает повторные попытки при сетевых ошибках.
parser/collect_products.py — основной скрипт: по списку запросов (молоко, хлеб, мясо и т.д.) получает товары, извлекает вес и КБЖУ и записывает категории и товары в базу.
parser/requirements.txt — зависимости парсера.
Инфраструктура (PostgreSQL и Redis) описана в отдельном файле docker-compose этой ветки.

##Таблицы базы

retailers — ритейлеры. Запись с кодом vkusvill должна существовать до запуска парсера.
categories — категории товаров, уникальны в паре «ритейлер + внешний ID».
products — товары с весом в граммах, единицей измерения и КБЖУ на 100 г. Уникальны в паре «ритейлер + внешний ID», при повторном запуске обновляются.

Схема создаётся из schema.sql, который должен лежать в корне ветки.

##Запуск

Заполните .env в корне репозитория (переменная DATABASE_URL). Путь к файлу можно переопределить через ENV_FILE.
Установите зависимости и запустите сбор:

```bash
pip install -r parser/requirements.txt
python parser/collect_products.py
```

Скрипт проходит по списку запросов с паузами, ошибки по отдельным товарам пишутся в лог и не останавливают сбор.
