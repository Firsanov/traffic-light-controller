# Traffic Light Control Service

Headless REST-сервис управления светофорами на городских перекрёстках.
Предоставляет API для симуляции работы перекрёстков и получения текущего
состояния сигналов.

---

## 1. Назначение сервиса

Сервис моделирует работу системы управления светофорами:

- хранит конфигурацию фаз для каждого перекрёстка;
- контролирует корректность и безопасность конфигурации
  (исключает конфликтующие зелёные сигналы);
- предоставляет REST API для:
  - чтения текущего состояния перекрёстка;
  - продвижения симуляции по времени (`tick`);
  - сброса состояния;
  - создания/обновления/удаления перекрёстков.

Предполагается использование в составе микросервисной архитектуры
для моделирования городского трафика.

---

## 2. Архитектура и зависимости

### Основные технологии

- Язык: **Python 3.11+**
- Web-фреймворк: **FastAPI**
- Типы и валидация: **Pydantic**
- Конфигурация: **pydantic-settings**
- Тестирование: **pytest**
- Линтер: **flake8**
- Code Style Fixer: **black**
- Git hooks: **pre-commit**
- Контейнеризация: **Docker**, **docker-compose**

### Архитектура

Приложение разделено на несколько слоёв:

- `app/core` — доменная логика:
  - `domain.py` — модель светофора, фазы, контроллер;
  - `repository.py` — in-memory хранилище перекрёстков;
  - `models.py` — Pydantic схемы для API;
  - `services.py` — сервисные операции для API;
  - `exceptions.py` — доменные исключения.
- `app/api` — HTTP слой:
  - `routes/intersections.py` — REST-эндпоинты для перекрёстков;
  - `deps.py` — зависимости (настройки, репозиторий).
- `app/config.py` — глобальные настройки (BaseSettings).
- `app/utils/logging.py` — конфигурация логирования.

### Взаимодействие с другими микросервисами

Сервис не зависит от других микросервисов, но предполагается, что:

- сервис симуляции трафика может вызывать эндпоинт
  `POST /api/v1/intersections/{id}/tick` для продвижения времени;
- сервис мониторинга может периодически опрашивать
  `GET /api/v1/intersections/{id}/state` для отображения состояния;
- оркестратор/health-check вызывает `GET /health`.

### Внешние сервисы

Специально **не используются** (нет S3/Redis/Kafka и т.п.), чтобы сосредоточиться
на программной инженерии управляющих систем и REST API.

---

## 3. Способы запуска сервиса

### 3.1. Локальный запуск без Docker

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Запуск сервиса
uvicorn app.main:app --reload
```

Сервис будет доступен по адресу: http://localhost:8000

### 3.2. Запуск через docker-compose

```bash
docker-compose up --build
```

Сервис будет доступен по адресу: http://localhost:8000

### 3.3. Переменные окружения

Поддерживаются следующие переменные окружения (через `.env` или напрямую):

- `APP_ENV` — окружение (`development` / `production`), по умолчанию `development`;
- `LOG_LEVEL` — уровень логирования (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

Пример `.env`:

```env
APP_ENV=development
LOG_LEVEL=DEBUG
```

---

## 4. API документация

После запуска приложения доступна встроенная документация:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Основные эндпоинты

#### Health-check

- `GET /health`

Ответ:

```json
{ "status": "ok" }
```

#### Список перекрёстков

- `GET /api/v1/intersections/`

Ответ:

```json
{
  "items": [
    {
      "id": "default",
      "name": "Main intersection"
    }
  ]
}
```

#### Текущее состояние перекрёстка

- `GET /api/v1/intersections/{id}/state`

Пример ответа:

```json
{
  "intersection_id": "default",
  "intersection_name": "Main intersection",
  "phase_name": "NS_GREEN",
  "elapsed_in_phase": 10,
  "phase_duration": 30,
  "signals": {
    "NS": "GREEN",
    "EW": "RED"
  }
}
```

#### Продвижение симуляции (`tick`)

- `POST /api/v1/intersections/{id}/tick`

Тело запроса:

```json
{ "seconds": 40 }
```

Пример ответа — аналогичен `GET /state`, но с обновлённым состоянием.

#### Сброс симуляции

- `POST /api/v1/intersections/{id}/reset`

Сбрасывает перекрёсток в первую фазу, `elapsed_in_phase = 0`.

#### Создание/обновление перекрёстка

- `PUT /api/v1/intersections/{id}`

Тело запроса:

```json
{
  "id": "my-intersection",
  "name": "Custom crossroad",
  "phases": [
    {
      "name": "NS_GREEN",
      "duration": 30,
      "states": {
        "NS": "GREEN",
        "EW": "RED"
      }
    },
    {
      "name": "NS_YELLOW",
      "duration": 5,
      "states": {
        "NS": "YELLOW",
        "EW": "RED"
      }
    },
    {
      "name": "EW_GREEN",
      "duration": 30,
      "states": {
        "NS": "RED",
        "EW": "GREEN"
      }
    },
    {
      "name": "EW_YELLOW",
      "duration": 5,
      "states": {
        "NS": "RED",
        "EW": "YELLOW"
      }
    }
  ]
}
```

Ответ содержит сохранённую конфигурацию.

#### Удаление перекрёстка

- `DELETE /api/v1/intersections/{id}`

Ответ: статус `204 No Content`.

---

## 5. Как тестировать

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Запуск тестов:

```bash
pytest
```

С Git hooks (pre-commit):

```bash
pre-commit install
```

Теперь при каждом `git commit` автоматически будут выполняться:

- форматирование кода (`black`);
- линтинг (`flake8`);
- unit-тесты (`pytest`).

---

## 6. Контакты и поддержка

Автор: **ИМЯ ФАМИЛИЯ**  
GitHub: https://github.com/your-username/traffic-light-controller

Обращения по ошибкам и предложения — через **GitHub Issues** репозитория.
