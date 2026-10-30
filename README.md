# Telegramm-Sport-Bot — Infrastructure (Ansible)

Инфраструктура как код (IaC) для развёртывания Telegram-бота, парсера,
PostgreSQL, Redis и мониторинга на двух серверах, соединённых приватной
сетью WireGuard.

Эта ветка содержит Ansible-плейбуки и роли для деплоя. Код бота и парсера
лежит в ветках `main` и `parser` соответственно.

## Ветки репозитория

| Ветка | Содержимое |
|---|---|
| `main` | Бот, мониторинг и CI/CD-деплой на сервер |
| `parser` | Парсер товаров, PostgreSQL и Redis (docker compose) |
| `ansible` (эта ветка) | Ansible-роли и плейбуки для развёртывания всей инфраструктуры |

## Архитектура

Два сервера, соединённые приватной сетью WireGuard `10.20.0.0/24`:

| Сервер | Группа в инвентаре | Что запущено | WireGuard IP |
|---|---|---|---|
| Парсер + БД | `PARSERSERV` (node1) | PostgreSQL 16, Redis 7 (Docker Compose), парсер (systemd timer) | `10.20.0.1` |
| Бот + мониторинг | `PRODSERV` (node2) | Telegram-бот, Prometheus, Grafana, Alertmanager, node-exporter (Docker Compose) | `10.20.0.2` |


Бот на `PRODSERV` подключается к PostgreSQL на `PARSERSERV` по внутреннему
WireGuard-адресу `10.20.0.1:5432` — порт не выставлен в интернет.

## Технологии

- Ansible 2.14+
- Docker, Docker Compose
- WireGuard
- systemd (юниты и таймеры для парсера)
- Prometheus, Alertmanager, Grafana, Node Exporter
- UFW, fail2ban

## Структура
├── ansible.cfg
├── inventory.ini # хосты и группы (PARSERSERV, PRODSERV)
├── host_vars/
│ ├── node1.yml # переменные для PARSERSERV
│ └── node2.yml # переменные для PRODSERV
├── playbooks/
│ └── playbook.yml # главный плейбук (3 play)
└── roles/
├── ping/ # проверка доступности хостов
├── common/ # базовые пакеты, timezone, UFW, fail2ban
├── wireguard/ # установка и настройка WireGuard
├── postgres_compose/ # PostgreSQL + Redis в Docker (node1)
├── parser/ # парсер + systemd service/timer (node1)
├── postgres_client/ # psql-клиент (node2)
└── tgbot/ # бот + мониторинг в Docker (node2)

## Роли

| Роль | Хосты | Назначение |
|---|---|---|
| `ping` | all | Проверка доступности хостов |
| `common` | all | Базовые пакеты, timezone, UFW, fail2ban |
| `wireguard` | all | Установка WireGuard, генерация ключей, конфиг `wg0` |
| `postgres_compose` | PARSERSERV | PostgreSQL 16 + Redis 7 в Docker Compose |
| `parser` | PARSERSERV | Парсер: venv, зависимости, systemd service + timer (каждые 12 ч) |
| `postgres_client` | PRODSERV | Установка `psql`-клиента для отладки |
| `tgbot` | PRODSERV | Бот, Prometheus, Grafana, Alertmanager, node-exporter в Docker |

## Переменные

Заполните `inventory.ini` и `host_vars/*.yml` реальными значениями.

### `inventory.ini`

```ini
[PARSERSERV]
node1 ansible_host=<NODE1_IP> ansible_user=<NODE1_USER> ansible_become=true

[PRODSERV]
node2 ansible_host=<NODE2_IP> ansible_user=<NODE2_USER> ansible_become=true
```

## Переменные

Заполните `inventory.ini` и `host_vars/*.yml` реальными значениями.

| Файл | Переменная | Описание |
|---|---|---|
| `host_vars/node1.yml` (PARSERSERV) | `wireguard_address` | WireGuard-адрес node1 (`10.20.0.1/24`) |
| `host_vars/node1.yml` (PARSERSERV) | `wireguard_listen_port` | Порт WireGuard (`51820`) |
| `host_vars/node1.yml` (PARSERSERV) | `wireguard_peers[].public_key` | Публичный ключ пира (node2) |
| `host_vars/node1.yml` (PARSERSERV) | `postgres_db`, `postgres_user`, `postgres_password` | Параметры PostgreSQL |
| `host_vars/node2.yml` (PRODSERV) | `wireguard_address` | WireGuard-адрес node2 (`10.20.0.2/24`) |
| `host_vars/node2.yml` (PRODSERV) | `wireguard_peers[].public_key` | Публичный ключ пира (node1) |
| `host_vars/node2.yml` (PRODSERV) | `wireguard_peers[].endpoint` | Публичный IP node1 и порт (`<NODE1_IP>:51820`) |
| `host_vars/node2.yml` (PRODSERV) | `tgbot_bind_address` | Адрес, на котором слушает бот (`10.20.0.2`) |
| `host_vars/node2.yml` (PRODSERV) | `tgbot_database_url` | URL подключения к PostgreSQL на node1 |
| `host_vars/node2.yml` (PRODSERV) | `tgbot_api` | Токен Telegram-бота (от @BotFather) |
| `host_vars/node2.yml` (PRODSERV) | `tgbot_grafana_admin_user`, `tgbot_grafana_admin_password` | Учётка администратора Grafana |
| `host_vars/node2.yml` (PRODSERV) | `tgbot_alertmanager_bot_token`, `tgbot_alertmanager_chat_id` | Бот и чат для алертов |

⚠️ **Секреты не коммитятся.** В репозитории — заглушки вида `<NODE1_PUB_KEY>`,
`<POSTGRES_PASSWORD>`, `<TELEGRAM_BOT_TOKEN>`. Реальные значения держите
локально или используйте `ansible-vault`.

## Запуск

### 1. Требования

- Ansible 2.14+
- Два сервера с Ubuntu 22.04/24.04, SSH-доступ, sudo
- Публичные IP для первого подключения
- Коллекции:

```bash
ansible-galaxy collection install community.general community.postgresql
```

### 2. Настройка 
Заполните inventory.ini и host_vars/node1.yml, host_vars/node2.yml

### 3. Проверка и деплой 
```bash
ansible-playbook -i inventory.ini playbooks/playbook.yml --syntax-check
ansible-playbook -i inventory.ini playbooks/playbook.yml --list-tasks
ansible-playbook -i inventory.ini playbooks/playbook.yml --check
ansible-playbook -i inventory.ini playbooks/playbook.yml
```

## Связаные ветки
main — код бота, мониторинг, CI/CD-деплой.
parser — парсер товаров, PostgreSQL и Redis.
