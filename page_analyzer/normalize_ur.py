from urllib.parse import urlparse, urlunparse


def normalize_url(url):
    '''Функция использует urlunparse для создания нового URL.
    В новом URL сохраняется:
    parsed_url.scheme: схема URL (например, http, https).
    parsed_url.hostname: хост (доменное имя) URL.
    Пустые строки для остальных компонентов (path, params, query, fragment).
    Например, если URL https://www.example.com/some/path?query=param#fragment,
    функция вернет https://www.example.com.'''
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.hostname, '', '', '', ''))
