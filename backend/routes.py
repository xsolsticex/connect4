from flask import render_template
from app import app

@app.route("/")
def game():
    return render_template("game.html", title="Juego")

@app.route("/partida/<nombre_streamer>")
def partida_por_streamer(nombre_streamer):
    return render_template("game.html", title=f"Partida de {nombre_streamer}", room_id=nombre_streamer)