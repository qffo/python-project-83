
from dotenv import load_dotenv
from .config import SECRET_KEY  # type: ignore
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)
from .unit import validate, perform_url_check
from .normalize_url import normalize_url


from .database import (
    get_all_urls,
    add_new_url,
    get_id_by_name,
    get_one_urls,
    get_checks_by_id
)


load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY


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


@app.post('/urls')
def add_url():
    url_name = request.form.get('url', '', type=str)
    url_name = normalize_url(url_name)
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


@app.post('/urls/<int:url_id>/checks')
def check_url(url_id):
    message, status_code, category = perform_url_check(url_id)

    if status_code == 404:
        return render_template('404.html'), 404

    flash(message, category)
    return redirect(url_for('one_url', url_id=url_id), 302)


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
