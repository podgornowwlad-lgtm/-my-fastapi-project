# FastAPI Microservices: ToDo & Short URL

Проект представляет собой два независимых микросервиса, реализованных с использованием FastAPI и SQLite, упакованных в Docker-контейнеры с сохранением данных через именованные Docker-тома.

Репозиторий предназначен для демонстрации навыков:
- разработки REST API;
- работы с FastAPI;
- использования SQLite;
- контейнеризации приложений с Docker;
- публикации кода и образов.

---

## Структура проекта

```
.
├── todo_app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── Dockerfile
├── shorturl_app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

---

## Используемые технологии

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- Docker
- Uvicorn

---

## ToDo Service

### Описание
Сервис управления списком задач с поддержкой CRUD-операций.
Данные хранятся в SQLite и сохраняются между перезапусками контейнера за счёт Docker volume.

### Эндпоинты

| Метод | URL | Описание |
|-----|-----|---------|
| POST | `/items` | Создание задачи |
| GET | `/items` | Получение всех задач |
| GET | `/items/{item_id}` | Получение задачи по ID |
| PUT | `/items/{item_id}` | Обновление задачи |
| DELETE | `/items/{item_id}` | Удаление задачи |

---

## Short URL Service

### Описание
Сервис сокращения URL.

### Эндпоинты

| Метод | URL | Описание |
|-----|-----|---------|
| POST | `/shorten` | Создание короткой ссылки |
| GET | `/{short_id}` | Редирект на полный URL |
| GET | `/stats/{short_id}` | Информация о ссылке |

---
## Локальный запуск

### ToDo-сервис

```bash
cd todo_app

python -m venv .venv
# Linux/macOS
source .venv/bin/activate  
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервис будет доступен по адресу: [http://localhost:8000](http://localhost:8000)

---

### URL Shortener

```bash
cd shorturl_app

python -m venv .venv
# Linux/macOS
source .venv/bin/activate  
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Сервис будет доступен по адресу: [http://localhost:8001](http://localhost:8001)

---
## Запуск с использованием Docker

```bash
docker volume create todo_data
docker volume create shorturl_data

docker run -d -p 8000:80 -v todo_data:/app/data todo-service
docker run -d -p 8001:80 -v shorturl_data:/app/data shorturl-service
```
## API документация

После запуска сервисов автоматическая интерактивная документация доступна по адресам:

- ToDo сервис: http://localhost:8000/docs
- URL Shortener сервис: http://localhost:8001/docs
---

## Вывод

В рамках проекта реализованы два FastAPI-микросервиса с хранением данных в SQLite,
контейнеризированные с использованием Docker.
Данные сохраняются между перезапусками контейнеров.
