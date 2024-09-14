import os
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

import psycopg2

load_dotenv()
app = Flask(__name__)  # Это callable WSGI-приложение
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


def get_all_urls():
    urls = []
    sql = """SELECT urls.id, urls.name, url_checks.created_at
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
                    'created_at': record[2]
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
def hello_world():
    return render_template('index.html')


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

    url_id = get_id_by_name(url_name)

    if not url_id:
        flash('Страница успешно добавлена', 'success')
        add_new_url(url_name)
        url_id = get_id_by_name(url_name)
    else:
        flash('Страница уже существует', 'info')

    return redirect(url_for('one_url', url_id=url_id), 302)


def sql_check_url(values):
    sql = '''
    INSERT INTO url_checks
    (url_id) VALUES (%s);
    '''
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (values,))
        conn.commit()


@app.post('/urls/<int:url_id>/checks')
def check_url(url_id):
    flash('Страница успешно проверена', 'success')
    sql_check_url(url_id)

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
        url_info['created_at'] = record[2]
    return url_info


def get_checks_by_id(url_id):
    url_checks = []
    query = '''
    SELECT
        url_checks.id,
        url_checks.created_at
    FROM url_checks
    WHERE url_checks.url_id = %s
    ORDER BY url_checks.id DESC;
    '''
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (url_id,))
        records = cursor.fetchall()
    if records:
        for record in records:
            url_checks.append(
                {'id': record[0],
                 'created_at': record[1]
                 }
            )
    return url_checks


@app.route('/urls/<int:url_id>')
def one_url(url_id):
    url_info = get_one_urls(url_id)
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
