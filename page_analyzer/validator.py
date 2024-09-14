import validators


# validators.url(url)
# функция проверяет, является ли переданная строка действительным URL.
# Если URL корректен, она возвращает True, в противном случае False.
def validate(url):
    if validators.url(url) and len(url) <= 255:
        return True
    return False
