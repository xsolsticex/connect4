import { setupSocketEvents } from './socket_handler.js';
import { initBoard, renderBoard } from './game_logic.js';
import { updateTurnUI } from './ui.js';

document.addEventListener("DOMContentLoaded", () => {
  renderBoard();
  initBoard();
  setupSocketEvents(updateTurnUI);
});