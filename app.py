"""Домашнє завдання #4
створіть веб-додаток з маршрутизацією для двох html сторінок: index.html та message.html
Також:
Обробіть під час роботи програми статичні ресурси: style.css, logo.png;
Організуйте роботу з формою на сторінці message.html;
У разі виникнення помилки 404 Not Found повертайте сторінку error.html
Ваша програма працює на порту 3000
==================================
Для роботи з формою створіть Socket сервер на порту 5000. 
Алгоритм роботи такий. Ви вводите дані у форму, вони потрапляють у ваш веб-додаток, 
який пересилає його далі на обробку за допомогою socket (протокол UDP), 
і зберігає його в json файл data.json в папку storage.
Socket серверу. Socket сервер переводить отриманий байт-рядок у словник 
Запустіть HTTP сервер і Socket сервер у різних потоках.
"""
import json
from datetime import datetime
import pathlib
import socket
from threading import Thread
from flask import Flask, request, render_template, send_from_directory, redirect

app = Flask(__name__)

BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.joinpath("storage")
DATA_FILE = DATA_DIR.joinpath("data.json")
STATIC_DIR = BASE_DIR.joinpath("static")
HOST = "127.0.0.1"
SERVER_PORT = 3000
SOCKET_PORT = 5000
ADDRESS = (HOST, SOCKET_PORT)


def create_dir_file():
    """Функція для створення папки та файлу, якщо вони поки що відсутні"""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir()

    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def send_to_socket_server(data):
    """Функція для обробки даних та надсилання їх на Socket сервер"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(json.dumps(data).encode("utf-8"), ADDRESS)


def socket_server():
    """Функція для обробки даних від Socket серверу"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(ADDRESS)
        while True:
            data, _ = s.recvfrom(1024)
            data_dict = json.loads(data.decode("utf-8"))
            # print("Received data from Socket server:", data_dict)

            with open(DATA_FILE, "r", encoding="utf-8") as datafile:
                data_json = json.load(datafile)

            data_json.update(data_dict)

            with open(DATA_FILE, "w", encoding="utf-8") as datafile:
                json.dump(data_json, datafile, ensure_ascii=False)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/message.html", methods=["GET"])
def message():
    return render_template("message.html")


@app.route("/message", methods=["POST"])
def submit():
    payload = {str(datetime.now()): dict(request.form.items())}

    create_dir_file()

    send_to_socket_server(payload)

    with open(DATA_FILE, "r", encoding="utf-8") as datafile:
        data_json = json.load(datafile)

    data_json.update(payload)

    for key, val in data_json.items():
        print("\033[90m>>> ", key, ": ", val, "\033[0m")

    with open(DATA_FILE, "w", encoding="utf-8") as datafile:
        json.dump(data_json, datafile, ensure_ascii=False)

    return redirect("/")


@app.route("/static/<path:filename>")
def static_file(filename):
    return send_from_directory(STATIC_DIR, filename)


@app.errorhandler(404)
def page_not_found(_):
    return render_template("error.html", error_code=404), 404


def http_server():
    app.run(debug=False, host=HOST, port=SERVER_PORT)


if __name__ == "__main__":
    socket_thread = Thread(target=socket_server)
    socket_thread.start()

    http_server()
