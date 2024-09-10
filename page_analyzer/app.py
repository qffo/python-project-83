import os
from flask import Flask

# Это callable WSGI-приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello_world():
    return 'Welcome to World!'
