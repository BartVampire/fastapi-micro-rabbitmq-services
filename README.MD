# 🌐 FastAPI Microservices Project (test)

![Docker](https://camo.githubusercontent.com/a1b0d308fd81d69d6cb59b067d1aa0d24ad250494bbe15d7e00086315e77ce59/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f636b65722d3234393645443f7374796c653d666f722d7468652d6261646765266c6f676f3d646f636b6572266c6f676f436f6c6f723d7768697465) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white) 
![PostgreSQL](https://camo.githubusercontent.com/1888bcda4a734ecca51d2c9315781cd7df8ff627d302e4447dbf9596b84842ab/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f506f737467726553514c2d3333363739313f7374796c653d666f722d7468652d6261646765266c6f676f3d706f737467726573716c266c6f676f436f6c6f723d7768697465) ![Redis](https://camo.githubusercontent.com/c04bf776f4585a9abf246a25bb8a98375f56bcce8ca144ec266a9c13010f3e33/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f52656469732d4443333832443f7374796c653d666f722d7468652d6261646765266c6f676f3d7265646973266c6f676f436f6c6f723d7768697465)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-ff6b05?style=for-the-badge&logo=RabbitMQ&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-009688?style=for-the-badge&logo=nginx&logoColor=white)
![KrakenD](https://img.shields.io/badge/krakend-009688?style=for-the-badge&logo=krakend&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=HTML5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=CSS3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=Poetry&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=Swagger&logoColor=black)

## ✨ О проекте

Данный проект реализует систему микросервисов для аутентификации и управления пользователями. Основные особенности:

- **Микросервис `auth`:**
  - Аутентификация и авторизация через cookies (access и refresh токены).
  - HTML-страница для входа, построенная с использованием **Jinja2**, CSS и JS.
  - Взаимодействие с базой данных PostgreSQL через Docker.
  - RabbitMQ для обработки пользовательских данных при регистрации.

- **Микросервис `user`:**
  - Регистрация пользователей, обновление данных, получение информации, удаление аккаунтов.
  - Redis для дополнительного кэширования (по желанию).
  - HTML-страница для регистрации с использованием **Jinja2**, CSS и JS.

- **API Gateway с помощью KrakenD:**
  - Проверка токенов на эндпоинтах.
  - Перенаправление запросов на соответствующие микросервисы.

- **Nginx:**
  - Управление маршрутами.
  - Работа со статическими файлами.
  - Подключен ratelimiter для защиты от DDoS.

- **Docker Compose:**
  - Простая настройка и развертывание всех сервисов.
  - Portainer для управления контейнерами.

- **RabbitMQ:**
  - Асинхронное взаимодействие между сервисами через обменник `user_exchange` (FANOUT).

---
⚙️ Переменные окружения

- Для сервиса auth и user:
```
FASTAPI__DB__URL=...
POSTGRES_HOST=...
POSTGRES_PASSWORD=...
FASTAPI__FIRST__PEPPER=...
FASTAPI__SECOND__PEPPER=...
FASTAPI__THIRD__PEPPER=...
```
- Для user (опционально Redis):
```
FASTAPI__REDIS__HOST=...
FASTAPI__REDIS__PORT=...
FASTAPI__REDIS__DB=...
FASTAPI__REDIS__PASSWORD=...
```
---

> Приятного использования!


