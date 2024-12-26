from starlette.templating import Jinja2Templates
templates = Jinja2Templates(directory="jinja2_api/templates")


def https_url(url):
    url = str(url)  # Преобразуем объект URL в строку
    if url.startswith("http:"):
        return url.replace("http:", "https:")
    return url


# Регистрация фильтра
templates.env.filters["https_url"] = https_url