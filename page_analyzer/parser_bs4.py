import requests
from bs4 import BeautifulSoup


def get_h1(url):
    response = requests.get(url)
    if response.status_code == 200:
        return get_h1_from_html(response.text)
    else:
        raise Exception(
            f'Ошибка при получении страницы: {response.status_code}')


def get_h1_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1_tag = soup.find('h1')
    return h1_tag.text if h1_tag else ''


def get_title(url):
    response = requests.get(url)
    if response.status_code == 200:
        return get_title_from_html(response.text)
    else:
        raise Exception(
            f'Ошибка при получении страницы: {response.status_code}')


def get_title_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    title_tag = soup.find('title')
    return title_tag.text if title_tag else ''


def get_descr(url):
    response = requests.get(url)
    if response.status_code == 200:
        return get_descr_from_html(response.text)
    else:
        raise Exception(
            f'Ошибка при получении страницы: {response.status_code}')


def get_descr_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    descr_tag = soup.find('meta', attrs={'name': 'description'})
    if descr_tag and 'content' in descr_tag.attrs:
        content_value = descr_tag['content']
        return content_value
    else:
        return ''
