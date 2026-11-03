const $ = (id) => document.getElementById(id);
let ws = null, myName = "", countdownEnd = null, turnTotal = 10;

async function enter(path) {
  const name = $("name").value.trim();
  $("error").textContent = "";
  if (!name) { $("error").textContent = "Enter your name first."; return; }
  try {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name })
    });
    const data = await res.json();
    if (!res.ok) {
      $("error").textContent = typeof data.detail === "string" ? data.detail : "Something went wrong.";
      return;
    }
    myName = name;
    connect(data.room_code, data.player_id);
  } catch (err) {
    $("error").textContent = "Could not reach the server.";
  }
}

function connect(code, playerId) {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/${code}/${playerId}`);
  ws.onopen = () => {
    $("join-view").classList.add("hidden");
    $("game-view").classList.remove("hidden");
    $("room-code").textContent = code;
  };
  ws.onmessage = (e) => render(JSON.parse(e.data));
  ws.onclose = () => {
    if ($("game-view").classList.contains("hidden")) {
      $("error").textContent = "Could not connect to that room.";
    } else {
      $("status").textContent = "Connection lost. Refresh the page to rejoin.";
      $("word").disabled = true;
      $("submit-btn").disabled = true;
      countdownEnd = null;
    }
  };
}

function render(s) {
  const mine = s.current_turn === myName;
  const me = s.players.find((p) => p.name === myName);

  const list = $("players");
  list.replaceChildren();
  for (const p of s.players) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = p.name + (p.name === myName ? " (you)" : "");
    if (!p.is_alive) chip.classList.add("dead");
    if (s.is_started && !s.is_over && p.name === s.current_turn) chip.classList.add("turn");
    list.appendChild(chip);
  }

  const tiles = $("letters");
  tiles.replaceChildren();
  if (s.is_started && !s.is_over && s.letters) {
    for (const ch of s.letters) {
      const t = document.createElement("div");
      t.className = "tile";
      t.textContent = ch;
      tiles.appendChild(t);
    }
  }

  $("start-btn").classList.toggle("hidden", s.is_started || s.host !== myName);
  $("banner").classList.toggle("hidden", !s.is_over);
  if (s.is_over) $("banner").textContent = s.winner === myName ? "You win!" : `${s.winner} wins!`;

  let status;
  if (!s.is_started) status = s.host === myName ? "You’re the host. Start when everyone has joined." : "Waiting for the host to start…";
  else if (s.is_over) status = "Game over";
  else if (me && !me.is_alive) status = "You’re out. Watching the rest…";
  else status = mine ? "Your turn!" : `${s.current_turn}’s turn`;
  $("status").textContent = status;

  const canPlay = s.is_started && !s.is_over && mine;
  $("word").disabled = !canPlay;
  $("submit-btn").disabled = !canPlay;
  if (canPlay) $("word").focus();

  if (s.seconds_left === null) {
    countdownEnd = null;
    $("timer").textContent = "";
    $("bar").firstElementChild.style.width = "0";
  } else {
    turnTotal = Math.max(10, s.seconds_left);
    countdownEnd = performance.now() + s.seconds_left * 1000;
  }
}

setInterval(() => {
  if (countdownEnd === null) return;
  const left = Math.max(0, (countdownEnd - performance.now()) / 1000);
  $("timer").textContent = left.toFixed(1) + "s";
  $("bar").firstElementChild.style.width = (left / turnTotal * 100) + "%";
  $("bar").classList.toggle("low", left <= 3);
}, 100);

function submitWord() {
  const word = $("word").value.trim();
  if (!word || !ws) return;
  ws.send(JSON.stringify({ type: "submit_word", word }));
  $("word").value = "";
}

$("create-btn").onclick = () => enter("/rooms");
$("join-btn").onclick = () => {
  const code = $("code").value.trim().toUpperCase();
  if (!code) { $("error").textContent = "Enter a room code."; return; }
  enter(`/rooms/${encodeURIComponent(code)}/join`);
};
$("start-btn").onclick = () => ws.send(JSON.stringify({ type: "start" }));
$("submit-btn").onclick = submitWord;
$("word").addEventListener("keydown", (e) => { if (e.key === "Enter") submitWord(); })