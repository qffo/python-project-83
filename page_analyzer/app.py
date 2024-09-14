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
    sql = "SELECT id, name FROM urls ORDER BY id DESC;"
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

    add_new_url(url_name)
    url_id = get_id_by_name(url_name)
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


@app.route('/urls/<int:url_id>')
def one_url(url_id):
    url_info = get_one_urls(url_id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'one_url.html',
        messages=messages,
        url=url_info,
    )


@app.get('/urls')
def get_urls():
    return render_template('all_urls.html')


if __name__ == '__main__':
    app.run()
