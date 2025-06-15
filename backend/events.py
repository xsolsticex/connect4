import asyncio
import time
from flask import request
from flask_socketio import emit, join_room
from backend.app import socket
from backend.gestor_partidas import GestorPartidas

partidas_manager = GestorPartidas()

@socket.on("connect")
def handle_connect():
    client_id = request.sid
    emit("server-message", {"msg": f"Conectado: {client_id}"}, to=client_id)

@socket.on("join")
def join_handler(data):
    room_id = data["room_id"]
    username = data["username"].lower()
    join_room(room_id)

    partida = partidas_manager.obtener_partida(room_id)
    jugadores = partida["jugadores"]

    # Añadir jugador si hay hueco
    if username not in jugadores and len(jugadores) < 2:
        jugadores.append(username)
        print(f"[JUGADORES EN {room_id}] {jugadores}")

    # Si aún no hay dos jugadores
    if len(jugadores) < 2:
        emit("espera_jugador", {
            "show_modal": True,
            "message": "Esperando a un segundo jugador..."
        }, room=room_id)

        # Emitir turno inicial para el primero
        emit("initial_player", {
            "player": jugadores[0],
            "color": "red",
            "room_id": room_id
        }, room=room_id)
        return  # 🔴 Aquí se corta, no sigue ejecutando

    # Ya hay 2 jugadores: ocultar modal
    emit("espera_jugador", { "show_modal": False }, room=room_id)

    # Emitir el turno actual solo una vez
    if partida.get("current") is None:
        partida["current"] = jugadores[0]  # Siempre empieza el primero
        color = "red"
    else:
        current = partida["current"]
        color = "red" if current == jugadores[0] else "yellow"

    emit("initial_player", {
        "player": partida["current"],
        "color": color,
        "room_id": room_id
    }, room=room_id)

@socket.on("obs_join_room")
def join_obs(data):
    room_id = data["room_id"]
    join_room(room_id)
    print(f"[OBS unido a la sala {room_id}]")

# @socket.on("drop")
# def handle_drop(data):
#     room_id = data.get("room_id")
#     username = data.get("username").lower()

#     partida = partidas_manager.obtener_partida(room_id)
#     if partida["current"] != username:
#         return

#     jugadores = partida["jugadores"]
#     color_actual = "red" if username == jugadores[0] else "yellow"

#     # Emitir el drop con el color correcto
#     emit("drop", {
#         **data,
#         "color": color_actual
#     }, room=room_id)

#     # Cambiar turno
#     siguiente = jugadores[1] if username == jugadores[0] else jugadores[0]
#     partida["current"] = siguiente
#     color_siguiente = "red" if siguiente == jugadores[0] else "yellow"

#     emit("cambio_turno", {
#         "player": siguiente,
#         "color": color_siguiente,
#         "room_id": room_id
#     }, room=room_id)
@socket.on("drop")
def handle_drop(data):
    room_id = data.get("room_id")
    username = data.get("username").lower()
    columna = data.get("column") - 1  # Ajuste por 0-indexado

    partida = partidas_manager.obtener_partida(room_id)
    if partida["current"] != username:
        return

    jugadores = partida["jugadores"]
    color_actual = "red" if username == jugadores[0] else "yellow"
    tablero = partida.setdefault("tablero", [[None for _ in range(7)] for _ in range(6)])

    fila = obtener_fila_disponible(tablero, columna)
    if fila is None:
        return  # Columna llena

    # Actualizar tablero con el nuevo movimiento
    tablero[fila][columna] = color_actual

    # Emitir el drop con la posición
    emit("drop", {
        **data,
        "color": color_actual,
        "column": columna + 1  # Volver a 1-indexado si es necesario
    }, room=room_id)

    # Verificar si el jugador ha ganado
    if jugador_gana(tablero, color_actual):
        emit("victoria", {
            "player": username,
            "color": color_actual,
            "room_id": room_id
        }, room=room_id)
        return  # No cambiar turno si alguien ganó

    # Cambiar turno
    siguiente = jugadores[1] if username == jugadores[0] else jugadores[0]
    partida["current"] = siguiente
    color_siguiente = "red" if siguiente == jugadores[0] else "yellow"
    time.sleep(2)

    emit("cambio_turno", {
        "player": siguiente,
        "color": color_siguiente,
        "room_id": room_id
    }, room=room_id)

def obtener_fila_disponible(tablero, col):
    for row in reversed(range(6)):
        if tablero[row][col] is None:
            return row
    return None

def jugador_gana(tablero, color):
    return (
        comprobar_filas(tablero, color) or
        comprobar_columnas(tablero, color) or
        comprobar_diagonales(tablero, color)
    )
def comprobar_diagonales(tablero, color):
    # Diagonales ↘
    for row in range(3):
        for col in range(4):
            if all(tablero[row+i][col+i] == color for i in range(4)):
                return True

    # Diagonales ↙
    for row in range(3, 6):
        for col in range(4):
            if all(tablero[row-i][col+i] == color for i in range(4)):
                return True

    return False
def comprobar_filas(tablero, color):
    for row in tablero:
        contador = 0
        for celda in row:
            if celda == color:
                contador += 1
                if contador == 4:
                    return True
            else:
                contador = 0
    return False
def comprobar_columnas(tablero, color):
    for col in range(7):
        contador = 0
        for row in range(6):
            if tablero[row][col] == color:
                contador += 1
                if contador == 4:
                    return True
            else:
                contador = 0
    return False

@socket.on("test_win")
def test_win(data):
    room_id = data.get("room_id")
    username = data.get("username").lower()
    partida = partidas_manager.obtener_partida(room_id)

    # Simular jugadas alternadas hasta una victoria horizontal para red
    jugadas = [0, 0, 1, 1, 2, 2, 3]  # columnas (victoria en 0-1-2-3)

    for i, col in enumerate(jugadas):
        user = partida["jugadores"][i % 2]
        color = "red" if user == partida["jugadores"][0] else "yellow"
        fila = obtener_fila_disponible(partida["tablero"], col)
        if fila is None:
            continue
        partida["tablero"][fila][col] = color

        emit("drop", {
            "username": user,
            "column": col + 1,
            "room_id": room_id,
            "color": color
        }, room=room_id)

        if jugador_gana(partida["tablero"], color):
            emit("victoria", {
                "player": user,
                "color": color,
                "room_id": room_id
            }, room=room_id)
            break

    partida["current"] = partida["jugadores"][1]

@socket.on("win")
def handle_win(data):
    room_id = data.get("room_id")
    emit("win", data, room=room_id)

@socket.on("change_color")
def handle_change_color(data):
    room_id = data.get("room_id")
    emit("change_color", data, room=room_id)

@socket.on("fin")
def handle_fin(data):
    room_id = data.get("room_id")
    emit("fin", data, room=room_id)

@socket.on("restart")
def handle_restart(data):
    room_id = data.get("room_id")
    partidas_manager.reiniciar_partida(room_id)
    emit("restart", data, room=room_id)

@socket.on("cambio_turno")
def handle_cambio_turno(data):
    print("Entra en el cambio de turno")
    room_id = data.get("room_id")
    partida = partidas_manager.obtener_partida(room_id)
    jugadores = partida["jugadores"]
    if len(jugadores) < 2:
        emit("espera_jugador", {"message": "Esperando a que un jugador se una...", "show_modal": True}, room=room_id)
        return
    current = partida["current"]
    siguiente = jugadores[1] if current == jugadores[0] else jugadores[0]
    partida["current"] = siguiente
    color = "red" if siguiente == jugadores[0] else "yellow"
    emit("cambio_turno", {"player": siguiente, "color": color, "room_id": room_id}, room=room_id)
    emit("initial_player", {"player": siguiente, "color": color, "room_id": room_id}, room=room_id)