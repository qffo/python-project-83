import validators
import logging
import requests
from .parser_bs4 import get_h1, get_title, get_descr
from .database import (
    get_one_url,
    sql_check_url,
)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def validate(url: str) -> bool:
    """
    Check if the URL is valid.
    """
    return validators.url(url) and len(url) <= 255


def perform_url_check(url_id):
    """
    Check the status of a URL and save the results to the database.
    """
    url_info = get_one_url(url_id)

    if not url_info:
        return None, 404

    try:
        response = requests.get(url_info['name'])
        response.raise_for_status()

    except Exception:
        return 'Произошла ошибка при проверке', 500, 'danger'

    bs4_h1 = get_h1(response)
    bs4_title = get_title(response)
    bs4_descr = get_descr(response)

    sql_check_url(url_id, response.status_code,
                  bs4_h1, bs4_title, bs4_descr)

    return 'Страница успешно проверена', 200, 'success'
