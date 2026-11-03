const $ = (id) => document.getElementById(id);
let ws = null, myName = "", countdownEnd = null, turnTotal = 10, session = null, retries = 0;

async function enter(path, nameId) {
  const name = $(nameId).value.trim();
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
    localStorage.setItem("relay_session", JSON.stringify({ code: data.room_code, playerId: data.player_id, name }));
    connect(data.room_code, data.player_id);
  } catch (err) {
    $("error").textContent = "Could not reach the server.";
  }
}

  function connect(code, playerId) {
  if (ws) { ws.onclose = null; ws.close(); }
  session = { code, playerId };
  let opened = false;
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/${code}/${playerId}`);
  ws.onopen = () => {
    opened = true;
    retries = 0;
    $("join-view").classList.add("hidden");
    $("game-view").classList.remove("hidden");
    $("room-code").textContent = code;
  };
  ws.onmessage = (e) => render(JSON.parse(e.data));
  ws.onclose = () => {
    if (!session) return;
    if (!opened && ++retries >= 8) { leaveRoom("Could not rejoin that room."); return; }
    $("status").textContent = "Connection lost. Reconnecting…";
    $("word").disabled = true;
    $("submit-btn").disabled = true;
    countdownEnd = null;
    setTimeout(reconnect, 2000);
  };
}

   async function reconnect() {
     if (!session) return;
     try {
       const res = await fetch(`/rooms/${encodeURIComponent(session.code)}`);
       if (res.status === 404) { leaveRoom("That room no longer exists."); return; }
     } catch (err) { /* server not reachable yet, try again below */ }
     connect(session.code, session.playerId);
   }

   function leaveRoom(msg) {
     retries = 0;
     session = null;
     localStorage.removeItem("relay_session");
     $("game-view").classList.add("hidden");
     $("join-view").classList.remove("hidden");
     $("error").textContent = msg;
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
  $("restart-btn").classList.toggle("hidden", !s.is_over);
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
  const feed = $("feed");
  feed.replaceChildren();
  for (const ev of [...s.events].reverse()) {
     const who = ev.player === myName ? "You" : ev.player;
     let text;
     if (ev.ok) text = `${who}: ${ev.word} ✓`;
     else if (ev.reason === "left the game") text = `${who} left the game`;
     else if (!ev.word) text = `${who} ran out of time, out!`;
     else text = `${who} typed ${ev.word}: ${ev.reason}, out!`;
     const row = document.createElement("div");
     row.className = "event " + (ev.ok ? "ok" : "bad");
     row.textContent = text;
     feed.appendChild(row);
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

$("create-btn").onclick = () => enter("/rooms", "create-name");
$("join-btn").onclick = () => {
  const code = $("code").value.trim().toUpperCase();
  if (!code) { $("error").textContent = "Enter a room code."; return; }
  enter(`/rooms/${encodeURIComponent(code)}/join`, "join-name");
};
$("start-btn").onclick = () => ws.send(JSON.stringify({ type: "start" }));
$("submit-btn").onclick = submitWord;
$("word").addEventListener("keydown", (e) => { if (e.key === "Enter") submitWord(); })

$("restart-btn").onclick = () => ws.send(JSON.stringify({ type: "restart" }));
$("home-btn").onclick = () => {
     if (ws) {
       ws.onclose = null;
       if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "leave" }));
     }
     leaveRoom("");
   };

try {
     const saved = JSON.parse(localStorage.getItem("relay_session"));
     if (saved) {
       myName = saved.name;
       session = { code: saved.code, playerId: saved.playerId };
       reconnect();
     }
   } catch (err) {}