let currentPlayer = null;
let currentColor = "red";
const board = document.getElementById("gameboard");
const rows = 6;

export function setCurrentPlayer(player) {
  currentPlayer = player;
}

export function setCurrentColor(color) {
  currentColor = color;
}

export function renderBoard() {
  board.innerHTML = "";
  for (let row = 0; row < 6; row++) {
    for (let column = 0; column < 7; column++) {
      const cell = document.createElement("div");
      cell.classList.add("cell");
      cell.dataset.row = row;
      cell.dataset.col = column;
      board.appendChild(cell);
    }
  }
}

export function initBoard() {
  document.querySelectorAll(".cell").forEach((cell) => {
    cell.addEventListener("click", (e) => {
      if (board.style.pointerEvents === "none") return;
      const col = e.target.dataset.col;
      if (col) {
        const socket = io();
        socket.emit("drop", {
          username: currentPlayer,
          column: parseInt(col),
          room_id: document.body.dataset.room,
          simulated:true
        });
      }
    });
  });

  board.addEventListener("mousemove", (e) => {
    const rect = board.getBoundingClientRect();
    const colWidth = rect.width / 7;
    const col = Math.floor((e.clientX - rect.left) / colWidth);
    const floatingDisc = document.getElementById("floatingDisc");
    floatingDisc.style.transform = `translateX(${col * colWidth}px)`;
  });
}

async function move(col, delay = 100) {
  return new Promise((resolve) => {
    const rect = board.getBoundingClientRect();
    const colWidth = rect.width / 7;

    const targetX = col * colWidth;

    const currentTransform = floatingDisc.style.transform;
    const currentX = currentTransform.includes("translateX")
      ? parseFloat(currentTransform.replace("translateX(", "").replace("px)", ""))
      : 0;

    if (Math.abs(currentX - targetX) < 1) {
      console.log("La ficha ya está en la posición deseada:", currentX);
      resolve();
      return;
    }

    floatingDisc.removeEventListener("transitionend", resolve);

    setTimeout(() => {
      floatingDisc.style.transition = `transform 0.3s ease`;
      floatingDisc.style.transform = `translateX(${targetX}px)`;

      floatingDisc.addEventListener(
        "transitionend",
        () => {
          console.log("Movimiento completado a:", targetX);
          resolve();
        },
        { once: true }
      );
    }, delay);
  });
}

export async function dropDisc(data) {
  const col = data.column - 1;

  const row = findDropPosition(col);
  if (row === null) return;
  await move(col)
  const cell = board.querySelector(`[data-row="${row}"][data-col="${col}"]`);
  const disc = document.createElement("div");
  disc.classList.add("disc", currentColor);
  const content = document.createElement("div");
  content.classList.add("disc-content", currentColor + "-content");
  disc.appendChild(content);
  cell.appendChild(disc);

  disc.style.transform = `translateY(-${(row + 1) * 60}px)`;
  setTimeout(() => (disc.style.transform = "translateY(0)"), 50);
}

export function findDropPosition(col) {
  for (let row = rows - 1; row >= 0; row--) {
    const cell = board.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (!cell.hasChildNodes()) return row;
  }
  return null;
}

export function resetTurno() {
  currentPlayer = null;
  currentColor = "red";
}

export function updateDiscColor(color) {
  const floatingDisc = document.getElementById("floatingDisc");
  const discContent = document.getElementById("discContent");
  floatingDisc.className = "floating-disc";
  discContent.className = "disc-content";
  if (color === "yellow") {
    floatingDisc.classList.add("yellow");
    discContent.classList.add("yellow-content");
  } else {
    floatingDisc.classList.add("red");
    discContent.classList.add("red-content");
  }
}
