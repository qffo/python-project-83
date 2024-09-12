import os
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
)

import psycopg2

load_dotenv()
app = Flask(__name__)  # Это callable WSGI-приложение
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


def get_all_urls():
    urls = []
    sql = "SELECT id, name FROM urls;"
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


# @app.route('/')
# def index():
#     with psycopg2.connect(DATABASE_URL) as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * from urls;")
#         db_version = cursor.fetchone()
#     conn.close()
#     return f"{db_version}"


@app.get('/urls')
def get_urls():
    return render_template('all_urls.html')
