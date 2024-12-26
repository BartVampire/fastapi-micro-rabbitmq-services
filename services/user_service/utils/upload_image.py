import os
from fastapi import UploadFile
from .slug_generate import slugify

# Константы для работы с файлами
MEDIA_DIR = "media"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}
MAX_IMAGE_SIZE = 10_485_760  # 10MB в байтах


class ImageUploadError(Exception):
    """Исключение для ошибок при загрузке изображений"""

    pass


async def save_image(image: UploadFile, title: str) -> str:
    """
    Сохраняет загруженное изображение в папку media

    Args:
        image: Загруженный файл изображения
        title: Название услуги для генерации slug

    Returns:
        str: Путь к сохраненному файлу относительно папки media

    Raises:
        ImageUploadError: Если возникла ошибка при загрузке
    """
    # Проверяем тип файла
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise ImageUploadError(
            "Неподдерживаемый тип файла. Разрешены только JPEG и PNG"
        )

    # Создаем папку media если её нет
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)

    # Генерируем имя файла из slug названия услуги
    file_extension = os.path.splitext(image.filename)[1]
    slug = slugify(title)
    filename = f"{slug}{file_extension}"

    # Если файл с таким именем уже существует, добавляем числовой суффикс
    counter = 1
    original_filename = filename
    while os.path.exists(os.path.join(MEDIA_DIR, filename)):
        name_without_ext = os.path.splitext(original_filename)[0]
        filename = f"{name_without_ext}-{counter}{file_extension}"
        counter += 1

    file_path = os.path.join(MEDIA_DIR, filename)

    # Читаем и проверяем размер файла
    content = await image.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise ImageUploadError("Размер файла превышает 10MB")

    # Сохраняем файл
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise ImageUploadError(f"Ошибка при сохранении файла: {str(e)}")

    return filename


async def delete_image(filename: str) -> None:
    """Удаляет изображение из папки media"""
    if filename:
        file_path = os.path.join(MEDIA_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
