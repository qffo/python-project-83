import os
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)
from .validator import validate
from .normalize_ur import normalize_url
# from bs4 import BeautifulSoup
from .parser_bs4 import get_h1, get_title, get_descr

import psycopg2

load_dotenv()
app = Flask(__name__)  # Это callable WSGI-приложение
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


# форматируем дату в нормальную дату
# если дата проверки отсутствует то None
# если дата проверки есть то переводим её в нормальую дату
def data_format(created_at):
    if created_at is None:
        return None
    return created_at.date()


def get_all_urls():
    urls = []
    sql = """SELECT distinct on (urls.id)
    urls.id, urls.name, url_checks.created_at, url_checks.status_code
    FROM urls left join url_checks
    on urls.id = url_checks.url_id
    ORDER BY id DESC;"""
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
    if records:
        for record in records:
            urls.append(
                {
                    'id': record[0],
                    'name': record[1],
                    'created_at': data_format(record[2]),
                    'status_code': record[3]
                }
            )
    return urls


@app.get('/urls')
def all_urls():
    urls = get_all_urls()
    return render_template(
        'all_urls.html',
        urls=urls
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def add_new_url(url_name):
    query = 'INSERT INTO urls (name) VALUES (%s);'
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (url_name,))
        conn.commit()


def get_id_by_name(url_name):
    sql = '''
    SELECT id FROM urls
    WHERE name = %s;
    '''
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (url_name,))
        record = cursor.fetchone()
    url_id = record[0] if record else None
    return url_id


@app.post('/urls')
def add_url():
    url_name = request.form.get('url', '', type=str)
    if not validate(url_name):
        flash('Некорректный URL', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            messages=messages,
            url_name=url_name
        ), 422

    url_id = get_id_by_name(normalize_url(url_name))

    if not url_id:
        flash('Страница успешно добавлена', 'success')
        add_new_url(url_name)
        url_id = get_id_by_name(url_name)
    else:
        flash('Страница уже существует', 'info')

    return redirect(url_for('one_url', url_id=url_id), 302)


def get_one_urls(url_id):
    url_info = {}
    sql = 'SELECT * FROM urls WHERE id = %s;'
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (url_id,))
        record = cursor.fetchone()
    if record:
        url_info['id'] = record[0]
        url_info['name'] = record[1]
        url_info['created_at'] = data_format(record[2])
    return url_info


def sql_check_url(url_id, st_code, bs4_h1, bs4_title, bs4_descr):
    sql = '''
    INSERT INTO url_checks
    (url_id, status_code, h1, title, description)
    VALUES (%s, %s, %s, %s, %s);
    '''
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (url_id, st_code, bs4_h1, bs4_title, bs4_descr))
        conn.commit()


@app.post('/urls/<int:url_id>/checks')
def check_url(url_id):
    url_info = get_one_urls(url_id)

    if not url_info:
        return render_template('404.html'), 404

    # try - обработка возможных исключений, идёт вместе с except
    # В этом блоке выполняется код, который может вызвать исключение.
    try:
        r = requests.get(url_info['name'])

        # Метод resp.raise_for_status() проверяет, был ли запрос успешным
        # Если код состояния не 200 (например, 404 или 500),
        # будет вызвано исключение HTTPError
        r.raise_for_status()
        bs4_h1 = get_h1(url_info['name'])
        bs4_title = get_title(url_info['name'])
        bs4_descr = get_descr(url_info['name'])

        flash('Страница успешно проверена', 'success')
        sql_check_url(url_id, r.status_code, bs4_h1, bs4_title, bs4_descr)
        return redirect(url_for('one_url', url_id=url_id), 302)

    # except - Этот блок отлавливает все исключения, связанные с запросами,
    # и выполняет код внутри него, если произошло исключение
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('one_url', url_id=url_id))


def get_checks_by_id(url_id):
    url_checks = []
    sql = '''
    SELECT
        url_checks.id,
        url_checks.status_code,
        url_checks.created_at,
        url_checks.h1,
        url_checks.title,
        url_checks.description
    FROM url_checks
    WHERE url_checks.url_id = %s
    ORDER BY url_checks.id DESC;
    '''
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (url_id,))
        records = cursor.fetchall()
    if records:
        for record in records:
            url_checks.append(
                {'id': record[0],
                 'status_code': record[1],
                 'created_at': data_format(record[2]),
                 'h1': record[3],
                 'title': record[4],
                 'description': record[5]
                 }
            )
    return url_checks


@app.route('/urls/<int:url_id>')
def one_url(url_id):
    url_info = get_one_urls(url_id)
    if not url_info:
        return render_template('404.html'), 404
    messages = get_flashed_messages(with_categories=True)
    url_checks = get_checks_by_id(url_id)
    return render_template(
        'one_url.html',
        messages=messages,
        url=url_info,
        url_checks=url_checks
    )


@app.get('/urls')
def get_urls():
    return render_template('all_urls.html')


if __name__ == '__main__':
    app.run()
