from slugify import slugify as slugify_slug


def slugify(text):
    """
    Преобразует строку в slug формат

    Slugify:
    /text: Исходный текст, который вы хотите преобразовать в slug.
    /entities: Если True, HTML-сущности будут преобразованы в соответствующие символы.
    /decimal: Если True, HTML-десятичные коды будут преобразованы в соответствующие символы.
    /hexadecimal: Если True, HTML-шестнадцатеричные коды будут преобразованы в соответствующие символы.
    /max_length: Максимальная длина выходной строки. Если строка превышает эту длину, она будет обрезана.
    /word_boundary: Если True, строка будет обрезана до конца полного слова.
    /separator: Разделитель между словами в slug (по умолчанию -).
    /lowercase: Если True, все символы будут приведены к нижнему регистру.
    /allow_unicode: Если True, разрешает использование юникодных символов.
    """
    text = slugify_slug(
        text,
        separator="-",
        max_length=50,
        word_boundary=True,
        lowercase=True,
        allow_unicode=False,
    )
    return text
