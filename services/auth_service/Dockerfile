FROM python:3.12

#
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем nano редактор
RUN apt-get update && apt-get install -y nano


# Создаем рабочую директорию
RUN mkdir "/app"

# Устанавливаем рабочую директорию
WORKDIR "/app"

# Копируем зависимости в рабочую директорию
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем код в рабочую директорию
COPY . .

CMD ["alembic", "revision", "--autogenerate", "-m", "create tables"]
# Запускаем миграции с помощью команды
CMD ["alembic", "upgrade", "head"]

CMD ["gunicorn", "main:main_app", "--workers", "1", "--threads", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
