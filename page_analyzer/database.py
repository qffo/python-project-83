from psycopg2 import pool
from .config import DATABASE_URL  # type: ignore

connection_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)


def get_all_urls(conn=None):
    urls = []
    sql = """SELECT distinct on (urls.id)
    urls.id, urls.name, url_checks.created_at, url_checks.status_code
    FROM urls left join url_checks
    on urls.id = url_checks.url_id
    ORDER BY id DESC;"""

    conn = conn or connection_pool.getconn()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            records = cursor.fetchall()
        if records:
            for record in records:
                urls.append(
                    {
                        'id': record[0],
                        'name': record[1],
                        'created_at': (
                            record[2].date() if record[2] is not None else None
                        ),
                        'status_code': record[3]
                    }
                )
    finally:
        connection_pool.putconn(conn)
    return urls


def add_new_url(url_name, conn=None):
    sql = 'INSERT INTO urls (name) VALUES (%s);'

    conn = conn or connection_pool.getconn()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, (url_name,))
            conn.commit()
    finally:
        connection_pool.putconn(conn)


def get_id_by_name(url_name, conn=None):
    sql = '''
    SELECT id FROM urls
    WHERE name = %s;
    '''

    conn = conn or connection_pool.getconn()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, (url_name,))
            record = cursor.fetchone()
        url_id = record[0] if record else None
    finally:
        connection_pool.putconn(conn)
    return url_id


def get_one_url(url_id, conn=None):
    url_info = {}
    sql = 'SELECT * FROM urls WHERE id = %s;'

    conn = conn or connection_pool.getconn()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, (url_id,))
            record = cursor.fetchone()
        if record:
            url_info['id'] = record[0]
            url_info['name'] = record[1]
            url_info['created_at'] = record[2].date()
    finally:
        connection_pool.putconn(conn)
    return url_info


def sql_check_url(url_id, st_code, bs4_h1, bs4_title, bs4_descr, conn=None):
    sql = '''
    INSERT INTO url_checks
    (url_id, status_code, h1, title, description)
    VALUES (%s, %s, %s, %s, %s);
    '''
    conn = conn or connection_pool.getconn()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, (url_id, st_code, bs4_h1, bs4_title, bs4_descr))
            conn.commit()
    finally:
        connection_pool.putconn(conn)


def get_checks_by_id(url_id, conn=None):
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
    conn = conn or connection_pool.getconn()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, (url_id,))
            records = cursor.fetchall()
        if records:
            for record in records:
                url_checks.append(
                    {
                        'id': record[0],
                        'status_code': record[1],
                        'created_at': record[2].date(),
                        'h1': record[3],
                        'title': record[4],
                        'description': record[5]
                    }
                )
    finally:
        connection_pool.putconn(conn)
    return url_checks
