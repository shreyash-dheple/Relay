from game import Player, Room , load_word
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import random
import string
import uuid
import asyncio
import time

app = FastAPI()

#this is the time limit for each player's turn in seconds
TURN_SECONDS = 30
timers = {}      # room_code -> the running timer task
deadlines = {}   # room_code -> when the current turn runs out

#function to handle the turn timer for a room. It waits for the turn duration and then
#  automatically submits an empty word if the player hasn't submitted one
def cancel_timer(room_code):
    task = timers.pop(room_code, None)
    if task:
        task.cancel()
    deadlines.pop(room_code, None)

def start_timer(room):
    cancel_timer(room.room_code)
    deadlines[room.room_code] = time.monotonic() + TURN_SECONDS
    timers[room.room_code] = asyncio.create_task(
        turn_timer(room.room_code, room.current_turn)
    )

#function to process a submitted word for a room. It submits the word, checks 
# if the game is over, and either ends the game or starts a new round.
def process_word(room, word):
    room.submit_word(word)
    if room.is_game_over():
        room.is_over = True
        cancel_timer(room.room_code)
    else:
        room.start_round(prompt_words)
        start_timer(room)

async def turn_timer(room_code, turn_id):
    await asyncio.sleep(TURN_SECONDS)
    timers.pop(room_code, None)          # remove myself first
    room = rooms.get(room_code)
    if room is None or room.is_over or room.current_turn != turn_id:
        return
    process_word(room, "")               # empty word = fail = eliminated
    await manager.broadcast(room_code, build_state(room))

rooms = {}
prompt_words = load_word("words.txt")
valid_words = load_word("words_alpha.txt")


#This is a class to manage Websocket connections for each room.
class ConnectionManager:
    def __init__(self):
        self.connections = {}

    def add(self, room_code, player_id, websocket):
        self.connections.setdefault(room_code, {})[player_id] = websocket

    def remove(self, room_code, player_id):
        room_conns = self.connections.get(room_code, {})
        room_conns.pop(player_id, None)

    async def broadcast(self, room_code, message):
        for ws in list(self.connections.get(room_code, {}).values()):
            await ws.send_json(message)

#funnction to build the state of the room to send to frontend. 
def build_state(room):
    players = [
        {"name": p.name, "is_alive": p.is_alive}
        for p in room.players.values()
    ]
    current = None
    if room.current_turn is not None:
        current = room.players[room.current_turn].name

    winner = None
    if room.is_over:
        winner = room.get_winner().name

    seconds_left = None                                  #for the frontend to display a countdown timer for the current turn
    if room.room_code in deadlines:
        seconds_left = max(0, round(deadlines[room.room_code] - time.monotonic(), 1))


    host = next(iter(room.players.values())).name        #for the frontend to display who is the host of the room

    return {
        "type": "state",
        "players": players,
        "is_started": room.is_started,
        "is_over": room.is_over,
        "current_turn": current,
        "letters": room.current_letters,
        "winner": winner,
        "seconds_left": seconds_left,                    
        "host": host,   
    }

manager = ConnectionManager()

#this is a websocket endpoint for players to connect to a room and send/receive messages.
@app.websocket("/ws/{room_code}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, player_id: str):
    room = rooms.get(room_code)
    if room is None or player_id not in room.players:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    manager.add(room_code, player_id, websocket)
    name = room.players[player_id].name
    await manager.broadcast(room_code, build_state(room))

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "start":
                is_host = player_id == next(iter(room.players))
                if is_host and not room.is_started and len(room.players) >= 2:
                    room.is_started = True
                    room.next_turn()
                    room.start_round(prompt_words)
                    start_timer(room)            #start the turn timer for the first player

            elif msg_type == "submit_word":
                if room.is_started and not room.is_over and room.current_turn == player_id:
                    process_word(room, str(data.get("word", "")))      #process the submitted word and start a new turn or end the game

            await manager.broadcast(room_code, build_state(room))
    except WebSocketDisconnect:
        manager.remove(room_code, player_id)
        await manager.broadcast(room_code, build_state(room))

class NameRequest(BaseModel):
    name: str          

@app.post("/rooms")
def create_room(body: NameRequest):
    code = "".join(random.choices(string.ascii_uppercase, k=5))
    while code in rooms:
        code = "".join(random.choices(string.ascii_uppercase, k=5)) 

    
    room = Room(code)                    
    room.valid_words = valid_words  
    rooms[code] = room

    
    player_id = uuid.uuid4().hex[:8]                    
    player = Player(body.name, player_id) 
    room.add_player(player)

    
    return {"room_code": code, "player_id": player_id}

@app.get("/rooms/{room_code}")
def get_room(room_code: str):
    if room_code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms[room_code]
    names = [p.name for p in room.players.values()]
    return {"room_code": room_code, "players": names}

@app.post("/rooms/{room_code}/join")
def join_room(room_code: str, body: NameRequest):
    if room_code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms[room_code]

    if room.is_started:
        raise HTTPException(status_code=400, detail="Game already started")
    if body.name in [p.name for p in room.players.values()]:
            raise HTTPException(status_code=404, detail="Name already taken")
    

    player_id = uuid.uuid4().hex[:8]
    room.add_player(Player(body.name, player_id))

    return {"room_code": room_code, "player_id": player_id}