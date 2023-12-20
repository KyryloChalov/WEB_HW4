"""Домашнє завдання #4
створіть веб-додаток з маршрутизацією для двох html сторінок: index.html та message.html

Також:

Обробіть під час роботи програми статичні ресурси: style.css, logo.png;
Організуйте роботу з формою на сторінці message.html;
У разі виникнення помилки 404 Not Found повертайте сторінку error.html
Програма працює на порту 3000
"""
import json
from datetime import datetime
import pathlib
from flask import Flask, request, render_template, send_from_directory, redirect


app = Flask(__name__)

BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.joinpath("storage")
DATA_FILE = DATA_DIR.joinpath("data.json")
STATIC_DIR = BASE_DIR.joinpath("static")
SERVER_PORT = 3000
SOCKET_PORT = 5000


@app.route("/", methods=["GET"])
def index():
    """main сторінка index.html"""
    return render_template("index.html")


@app.route("/message.html", methods=["GET"])
def message():
    """сторінка message.html"""
    return render_template("message.html")


def create_dir_file():
    """створити папку storage та файл data.json, якщо їх ще нема"""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir()

    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


@app.route("/message", methods=["POST"])
def submit():
    """робота з формою на сторінці message.html
    запис введених у форму даних в json файл data.json в папку storage"""

    payload = {str(datetime.now()): dict(request.form.items())}

    create_dir_file()

    with open(DATA_FILE, "r", encoding="utf-8") as datafile:
        data_json = json.load(datafile)

    data_json.update(payload)

    # for key, val in data_json.items():
    #     print("\033[90m>>> ", key, ": ", val, "\033[0m")

    with open(DATA_FILE, "w", encoding="utf-8") as datafile:
        json.dump(data_json, datafile, ensure_ascii=False)

    return redirect("/")


@app.route("/static/<path:filename>")
def static_file(filename):
    """обробляємо статичні ресурси: style.css, logo.png"""
    return send_from_directory(STATIC_DIR, filename)


@app.errorhandler(404)
def page_not_found(_):
    """error 404 Not Found"""
    return render_template("error.html", error_code=404), 404


if __name__ == "__main__":
    app.run(debug=True, port=SERVER_PORT)
