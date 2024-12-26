import logging
import os
from datetime import datetime, UTC, timedelta

import bcrypt
import jwt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import HTTPException, status

from core import settings

logger = logging.getLogger(__name__)
load_dotenv()

key_token = os.getenv("FASTAPI__THIRD__PEPPER").encode()
cipher_suite = Fernet(key_token)


def hash_token(token: str) -> bytes:  # Функция хеширования токена
    encrypted_token_first = cipher_suite.encrypt(token.encode("utf-8"))
    encrypted_token_last = JOKE_PEPPER.upper() + encrypted_token_first + b"=ae"
    return encrypted_token_last


# Функция для дешифрования токена
def decrypt_token(encrypted_token: bytes | str) -> str:
    try:
        if type(encrypted_token) == str:
            encrypted_token = encrypted_token.encode()

        encrypted_token_first = encrypted_token[len(JOKE_PEPPER) : -3]
        decrypted_token = cipher_suite.decrypt(encrypted_token_first.decode("utf-8"))
        return decrypted_token.decode("utf-8")
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный токен."
        )


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth.private_key_path.read_text(),
    algorithm: str = settings.auth.algorithm,
    expire_minutes: int = settings.auth.access_token_expires_minutes,
    expire_timedelta: timedelta | None = None,
) -> bytes:  # Функция кодирования токена JWT с использованием RS256 алгоритма
    to_encode = payload.copy()
    now = datetime.now(UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    encoded = hash_token(encoded)

    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth.public_key_path.read_text(),
    algorithms: str = settings.auth.algorithm,
):  # Функция декодирования токена JWT с использованием RS256 алгоритма
    try:
        print(f"decode_jwt {type(token)}\n\n{token}\n\n")
        token = decrypt_token(token)
        decoded = jwt.decode(token, public_key, algorithms=[algorithms])
        return decoded
    except jwt.ExpiredSignatureError:
        logger.error("Токен истек")
        raise
    except jwt.InvalidTokenError:
        logger.error("Неправильный токен")
        raise
    except Exception as e:
        logger.exception(f"An error occurred during JWT decoding: {e}")
        raise


# Глобальная переменная для pepper (должна храниться в безопасном месте, например, в переменных окружения)
PEPPER = os.getenv("FASTAPI__FIRST__PEPPER").encode()
JOKE_PEPPER = os.getenv("FASTAPI__SECOND__PEPPER").encode()


def hash_password(password: str) -> bytes:  # Функция хеширования пароля
    salt = bcrypt.gensalt()
    peppered_password: bytes = password.encode() + PEPPER
    pwd_bytes_first: bytes = bcrypt.hashpw(peppered_password, salt)
    pwd_bytes_last: bytes = JOKE_PEPPER + pwd_bytes_first
    return pwd_bytes_last


def validate_password(
    password: str, hashed_password: bytes
) -> bool:  # Функция валидации пароля по хешу
    password = password.encode() + PEPPER
    hashed_password = hashed_password[5:]
    return bcrypt.checkpw(password=password, hashed_password=hashed_password)
