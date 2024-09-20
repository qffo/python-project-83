### Hexlet tests and linter status:
[![Actions Status](https://github.com/qffo/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/qffo/python-project-83/actions)
[![Actions Status](https://github.com/qffo/python-project-83/actions/workflows/pyci.yml/badge.svg)](https://github.com/qffo/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/046d5663336892bc4d57/maintainability)](https://codeclimate.com/github/qffo/python-project-83/maintainability)


## Описание

Page Analyzer – это сайт, который анализирует указанные страницы на SEO-пригодность.

https://python-project-83-7rqr.onrender.com

![пример GIF](/static/images/sample.gif)

## Minimum requirements for starting a project:
- Python version 3.10.15 or higher
- Pip version 24.2 or higher
- Poetry version 1.8.3

This project was built using these tools:

| Tool                                                          | Description                                             |
|---------------------------------------------------------------|---------------------------------------------------------|
| [poetry](https://python-poetry.org/)                          | "Python dependency management and packaging made easy"  |
| [flask](https://flask.palletsprojects.com/en/3.0.x/)          | "A set of tools for creating web applications"          |
| [gunicorn](https://gunicorn.org/)                             | "Python WSGI HTTP Server for UNIX"                      |
| [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc.ru/bs4ru.html/) | "library for parsing HTML and XML documents" |
|  |  |
| [flake8](https://flake8.pycqa.org/)                           | "Your tool for style guide enforcement"                 |
---

#### Клонирование репозитария
```
git clone git@github.com:qffo/python-project-83.git
cd python-project-83
```  
#### Создание базы данных
```
whoami
{username}
sudo -u postgres createuser --createdb {username} 
createdb {databasename}
psql {databasename} < database.sql
```  
#### Секретные ключи
Создать в директории page_analyzer .env файл для переменных окружения со следующей информацией:  
DATABASE_URL=postgresql://{username}:{password}@{host}:{port}/{databasename}  
SECRET_KEY='{your secret key}'
#### Установка зависимостей
```make install```  
#### Разработка и локальное использование
```make dev```  
#### Команды для деплоя
```
make build    
make start
```  