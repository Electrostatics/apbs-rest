import sys, os
from os import environ
from flask import Flask
import status_service
from flask_socketio import SocketIO

app = Flask(__name__)
app.register_blueprint(status_service.status_app)
socketio = status_service.status_socketio

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5002'))
    except ValueError:
        PORT = 5001

    socketio.init_app(app)
    socketio.run(app, HOST, PORT)