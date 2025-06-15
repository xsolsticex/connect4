import { dropDisc, resetTurno, updateDiscColor, setCurrentPlayer, setCurrentColor } from './game_logic.js';

export function setupSocketEvents(updateTurnUI) {
  const socket = io();
  const room_id = document.body.dataset.room;

socket.on("connect", () => {
  console.log("Conectado al servidor Socket.IO");

  if (room_id) {
    socket.emit("obs_join_room", { room_id });  // se une solo a escuchar
  }
});

  socket.on("drop", async (data) => {
    await dropDisc(data);
  });

  socket.on("initial_player", (data) => {
    console.log("Ha entrado")
    updateTurnUI(data);
    updateDiscColor(data.color);
    setCurrentPlayer(data.player);
    setCurrentColor(data.color);
  });

  socket.on("cambio_turno", (data) => {
    console.log(data)
    updateTurnUI(data);
    updateDiscColor(data.color);
    setCurrentPlayer(data.player);
    setCurrentColor(data.color);
  });

  socket.on("change_color", (data) => {
    document.querySelectorAll(".guia").forEach((g) => g.style.color = data.color);
    document.getElementById("actual").style.color = data.color;
  });

  socket.on("restart", () => {
    document.getElementById("modal").classList.remove("show");
    resetTurno();
    location.reload();
  });

  socket.on("victoria",(data)=>{
    console.log("mostar victoria")
    let player = data["player"]
    const modal = document.getElementById("modal");
    const message = document.getElementById("ganador");
    message.textContent = `Gana ${player}`
    modal.classList.add("show") 
  })

  socket.on("espera_jugador", (data) => {
    const modal = document.getElementById("modal");
    const message = document.getElementById("ganador");
    if (data.show_modal) {
      message.textContent = data.message;
      modal.classList.add("show");
    } else {
      modal.classList.remove("show");
    }
  });
}
