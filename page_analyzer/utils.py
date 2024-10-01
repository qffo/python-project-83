from enum import Enum
import psycopg2
import validators
import logging
import requests
from .parser_bs4 import get_h1, get_title, get_descr
from .database import (
    get_one_url,
    sql_check_url,
)


logging.basicConfig(
    level=logging.ERROR,
    filename="log.log",
    format="%(asctime)s %(levelname)s %(message)s",
    filemode='w'
)

logger = logging.getLogger(__name__)


def validate(url: str) -> bool:
    """
    Check if the URL is valid.
    """
    return validators.url(url) and len(url) <= 255


def perform_url_check(url_id):
    """
    Main function to check the status of a URL and save the results.
    """
    url_info, error_response = get_url_info_or_404(url_id)
    if error_response:
        return error_response

    response, error_response = fetch_url(url_info['name'])
    if error_response:
        return error_response

    bs4_h1, bs4_title, bs4_descr = parse_response(response, url_info['name'])

    save_to_database(url_id, response.status_code, bs4_h1, bs4_title, bs4_descr)

    return 'Страница успешно проверена', 200, 'success'


def get_url_info_or_404(url_id):
    """
    Get URL info or return a 404 error if not found.
    """
    url_info = get_one_url(url_id)
    if not url_info:
        return None, (None, 404)
    return url_info, None


def fetch_url(url):
    """
    Fetch the URL and handle request errors.
    """
    default_error_msg = 'Произошла ошибка при проверке'

    class ErrorMessage(str, Enum):
        httperror = 'HTTP error when checking the URL'
        connecterror = 'Connection error when checking the URL'
        timeout = 'Timeout when checking the URL'
        requestsexc = 'Exclusion from the request when checking the URL'

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response, None

    except requests.exceptions.HTTPError:
        logger.error(ErrorMessage.httperror, exc_info=True)
        return None, (default_error_msg, 500, 'danger')

    except requests.exceptions.ConnectionError:
        logger.error(ErrorMessage.connecterror, exc_info=True)
        return None, (default_error_msg, 500, 'danger')

    except requests.exceptions.Timeout:
        logger.error(ErrorMessage.timeout, extra=response)
        return None, (default_error_msg, 500, 'danger')

    except requests.exceptions.RequestException:
        logger.error(ErrorMessage.requestsexc, exc_info=True)
        return None, (default_error_msg, 500, 'danger')


def parse_response(response, url):
    """
    Parse the response to extract h1, title, and description.
    """
    try:
        bs4_h1 = get_h1(response)
        bs4_title = get_title(response)
        bs4_descr = get_descr(response)
        return bs4_h1, bs4_title, bs4_descr

    except (AttributeError, ValueError) as e:
        logger.error(
            f"{type(e).__name__} when parsing the URL {url}", exc_info=True)

    except Exception as e:
        logger.error(
            f"Error in URL analysis {url}: {str(e)}",
            exc_info=True)

    return None, None, None


def save_to_database(url_id, status_code, h1, title, descr):
    """
    Save the check result into the database.
    """
    try:
        sql_check_url(url_id, status_code, h1, title, descr)
    except psycopg2.DatabaseError:
        logger.error(
            f"DB error when saving URL with id {url_id}",
            exc_info=True)
    except Exception as e:
        logger.error(
            f"Error saving URL with id {url_id}: {str(e)}",
            exc_info=True
        )
