import os
from flask import Flask
from flask_socketio import SocketIO

from backend.data.environ_variable import socket_secret,gevent_support_enabled

os.environ["GEVENT_SUPPORT"] = gevent_support_enabled

app = Flask(__name__,template_folder="../templates", static_folder="../static")
app.config["SECRET_KEY"] = socket_secret

socket = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

from backend.routes import *
from backend.events import *

# if __name__ == "__main__":
from pyfiglet import Figlet
title = Figlet(font="slant")
print(title.renderText("server"))
socket.run(app, host="0.0.0.0",debug=False)