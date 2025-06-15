export function updateTurnUI({ player, color }) {
  const mod = document.getElementById("ganador");
  mod.textContent = `Es el turno de ${player}`;
  mod.style.color = color;
  const usu = document.getElementById("actual");
  usu.textContent = `Turno: ${player}`;
  usu.style.color = color;
}
