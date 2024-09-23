import requests
from bs4 import BeautifulSoup


def get_h1(url):
    # Получение HTML-кода страницы
    response = requests.get(url)

    # Проверка успешности запроса
    if response.status_code == 200:
        # Создание объекта BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск тега <h1>
        h1_tag = soup.find('h1')

        # Проверка наличия тега <h1> и вывод его содержимого
        if h1_tag:
            return h1_tag.text
        else:
            return ''
    else:
        return f'Ошибка при получении страницы: {response.status_code}'


def get_title(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.text
        else:
            return ''
    else:
        return f'Ошибка при получении страницы: {response.status_code}'


def get_descr(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        descr_tag = soup.find('meta', attrs={'name': 'description'})
        if descr_tag and 'content' in descr_tag.attrs:
            content_value = descr_tag['content']
            return content_value
        else:
            return ''
    else:
        return f'Ошибка при получении страницы: {response.status_code}'
