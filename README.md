# Task Management Service

Асинхронный сервис для управления задачами.

## Описание

Сервис предоставляет REST API для создания и управления задачами с асинхронной обработкой через RabbitMQ. Задачи обрабатываются в фоновом режиме с поддержкой приоритетов и параллельной обработки.

## Технологический стек

- **Python 3.10+**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM
- **PostgreSQL 14+** - база данных
- **RabbitMQ** - очередь сообщений
- **Alembic** - система миграций
- **pytest** - тестирование
- **Docker & Docker Compose** - контейнеризация

## Функциональность

### Статусы задач

- `NEW` - новая задача
- `PENDING` - ожидает обработки
- `IN_PROGRESS` - в процессе выполнения
- `COMPLETED` - завершено успешно
- `FAILED` - завершено с ошибкой
- `CANCELLED` - отменено

### Приоритеты задач

- `HIGH` - высокий приоритет
- `MEDIUM` - средний приоритет
- `LOW` - низкий приоритет

### API Endpoints

- `POST /api/v1/tasks` - создание задачи
- `GET /api/v1/tasks` - получение списка задач с фильтрацией и пагинацией
- `GET /api/v1/tasks/{task_id}` - получение информации о задаче
- `DELETE /api/v1/tasks/{task_id}` - отмена задачи
- `GET /api/v1/tasks/{task_id}/status` - получение статуса задачи

## Быстрый старт

### Предварительные требования

- Docker
- Docker Compose

### Запуск с Docker Compose

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd testwork
```

2. Скопируйте локальные переменные окружения:
```bash
cp .evn.example .env
```

3. Запустите сервисы:
```bash
sudo make startup
sudo make migrate
```

Сервисы будут доступны на:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

### Локальная разработка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Скопируйте и настройте переменные окружения:
```bash
cp .env.example .env
```

4. Запустите PostgreSQL и RabbitMQ (можно через Docker):
```bash
docker-compose up postgres rabbitmq
```

5. Примените миграции:
```bash
alembic upgrade head
```

6. Запустите API сервер:
```bash
uvicorn app.main:app --reload
```

7. В отдельном терминале запустите worker:
```bash
python -m app.worker.task_worker
```

## Тестирование

Запуск тестов:
```bash
pytest
```

Запуск с покрытием:
```bash
pytest --cov=app --cov-report=html
```

## Примеры использования

### Создание задачи

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Моя задача",
    "description": "Описание задачи",
    "priority": "HIGH"
  }'
```

### Получение списка задач

```bash
curl "http://localhost:8000/api/v1/tasks?page=1&page_size=10"
```

### Получение задачи по ID

```bash
curl "http://localhost:8000/api/v1/tasks/1"
```

### Отмена задачи

```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1"
```

### Получение статуса задачи

```bash
curl "http://localhost:8000/api/v1/tasks/1/status"
```

## Архитектура

### Структура проекта

```
.
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── tasks.py          # API endpoints
│   ├── core/
│   │   └── config.py             # Конфигурация
│   ├── db/
│   │   └── session.py            # Сессии БД
│   ├── models/
│   │   └── task.py               # SQLAlchemy модели
│   ├── schemas/
│   │   └── task.py               # Pydantic схемы
│   ├── services/
│   │   ├── task_service.py       # Бизнес-логика
│   │   └── queue_service.py      # RabbitMQ сервис
│   ├── worker/
│   │   └── task_worker.py        # Worker для обработки задач
│   └── main.py                   # FastAPI приложение
├── alembic/
│   ├── versions/                 # Миграции БД
│   └── env.py
├── tests/                        # Тесты
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

### Поток обработки задач

1. Клиент создает задачу через API
2. Задача сохраняется в PostgreSQL со статусом `PENDING`
3. Сообщение о задаче отправляется в RabbitMQ
4. Worker получает сообщение из очереди
5. Worker обновляет статус на `IN_PROGRESS`
6. Worker обрабатывает задачу
7. Worker обновляет статус на `COMPLETED` или `FAILED`

## Конфигурация

Основные параметры конфигурируются через переменные окружения (см. `.env.example`):

- `POSTGRES_*` - настройки PostgreSQL
- `RABBITMQ_*` - настройки RabbitMQ
- `MAX_CONCURRENT_TASKS` - максимальное количество одновременно обрабатываемых задач
- `TASK_PROCESSING_DELAY` - задержка обработки задачи (для демонстрации)

## Масштабирование

Для масштабирования можно:
1. Запустить несколько экземпляров worker
2. Увеличить `MAX_CONCURRENT_TASKS`
3. Использовать горизонтальное масштабирование API (несколько инстансов за балансировщиком)
