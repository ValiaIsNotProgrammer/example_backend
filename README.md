## Setup

Взять репу
```bash
git clone https://github.com/ValiaIsNotProgrammer/example_backend.git
```

**Для использования нужно создать .env файл**
```bash
cat .env.example > .env
```

Переменные уже готовы к использованию. Для компос использования использовать `DB__HOST=db` (по-умолчанию), без него - любой другой

Для запуска сервиса нужно поднять компос:

```bash
docker compose -f docker-compose.yml -p example_backend up
```

Либо локально создать базу данных `DB__NAME`, применять миграции
```bash
alembic upgrade head
```

И поднять FastAPI сервер
```bash
poetry run python3 main.py 
```

## Usage

- Для выполнения операций с клиентами необходим мастер токен. Он находится в файле .env.example и указан как API__MASTER_KEY. (в том числе и со статистикой)
- Доступ к ручкам posts предоставляется только через клиентские токены. Для получения пользователей с их токенами можно обратиться к `/clients/{id}` `/clients/list`
- Доступна Swagger документация по адресу `<host>:<port>/docs`


