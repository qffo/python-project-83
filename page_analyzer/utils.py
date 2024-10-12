from enum import Enum
import psycopg2
import validators
import logging.config
import requests
from page_analyzer.config import LOGGING_CONFIG
from .parser_bs4 import get_h1, get_title, get_descr
from .database import (
    get_one_url,
    sql_check_url,
)


logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING_CONFIG)


def validate(url: str) -> bool:
    """
    Check if the URL is valid.
    """
    return validators.url(url) and len(url) <= 255


class PageAnalyzerError(Exception):
    pass


class PageNotFound(PageAnalyzerError):
    pass


class PageCheckError(PageAnalyzerError):
    pass


def get_url_info(url_id: int) -> dict:
    """
    Get URL info or return None if not found.
    """
    url_info = get_one_url(url_id)
    if not url_info:
        return None
    return url_info


def perform_url_check(url_id: int) -> tuple:
    """
    Main function to check the status of a URL and handle the results.
    Raises custom exceptions in case of errors.
    """
    url_info = get_url_info(url_id)

    if not url_info:
        raise PageNotFound('URL not found')

    response = fetch_url(url_info['name'])
    if response is None:
        raise PageCheckError('Error checking the URL')

    bs4_h1, bs4_title, bs4_descr = parse_response(response, url_info['name'])

    save_to_database(url_id, response.status_code, bs4_h1, bs4_title, bs4_descr)

    return 'Страница успешно проверена', 200, 'success'


class ErrorMessage(str, Enum):
    httperror = 'HTTP error when checking the URL'
    connecterror = 'Connection error when checking the URL'
    timeout = 'Timeout when checking the URL'
    requestsexc = 'Request exception when checking the URL'


def fetch_url(url: str):
    """
    Fetch the URL and handle request errors.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError:
        logger.error(ErrorMessage.httperror, exc_info=True)
    except requests.exceptions.ConnectionError:
        logger.error(ErrorMessage.connecterror, exc_info=True)
    except requests.exceptions.Timeout:
        logger.error(ErrorMessage.timeout, exc_info=True)
    except requests.exceptions.RequestException:
        logger.error(ErrorMessage.requestsexc, exc_info=True)
    return None


class ParseError(Exception):
    """
    Custom exception for parsing errors.
    """
    pass


def parse_response(response, url: str):
    print(type(response))
    """
    Parse the response to extract h1, title, and description.
    """
    try:
        bs4_h1 = get_h1(response.text)
        bs4_title = get_title(response.text)
        bs4_descr = get_descr(response.text)
        return bs4_h1, bs4_title, bs4_descr

    except (AttributeError, ValueError) as e:
        logger.error(
            f"{type(e).__name__} when parsing the URL {url}", exc_info=True)
        raise ParseError(f"Error parsing the URL {url}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in URL analysis {url}: {str(e)}", exc_info=True)
        raise ParseError(f"Unexpected error parsing the URL {url}: {str(e)}")


def save_to_database(
        url_id: int,
        status_code: int,
        h1: str,
        title: str,
        descr: str
):
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
