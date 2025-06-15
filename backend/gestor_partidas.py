class GestorPartidas:
    def __init__(self):
        self.partidas = {}

    def obtener_partida(self, room_id):
        if room_id not in self.partidas:
            self.partidas[room_id] = {
                "connected_clients": {},
                "jugadores": [],
                "current": None,
                "color_asignado": {}
            }
        return self.partidas[room_id]

    def reiniciar_partida(self, room_id):
        self.partidas[room_id] = {
            "connected_clients": {},
            "jugadores": [],
            "current": None,
            "color_asignado": {}
        }