from game import Player, Room , load_word
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import random
import string
import uuid

app = FastAPI()

rooms = {}
prompt_words = load_word("words.txt")
valid_words = load_word("words_alpha.txt")


#This is a class to manage Websocket connections for each room.
class ConnectionManager:
    def __init__(self):
        self.connections = {}   # room_code -> {player_id: websocket}

    def add(self, room_code, player_id, websocket):
        self.connections.setdefault(room_code, {})[player_id] = websocket

    def remove(self, room_code, player_id):
        room_conns = self.connections.get(room_code, {})
        room_conns.pop(player_id, None)

    async def broadcast(self, room_code, message):
        for ws in list(self.connections.get(room_code, {}).values()):
            await ws.send_text(message)

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
    await manager.broadcast(room_code, f"{name} joined")

    try:
        while True:
            text = await websocket.receive_text()
            await manager.broadcast(room_code, f"{name}: {text}")
    except WebSocketDisconnect:
        manager.remove(room_code, player_id)
        await manager.broadcast(room_code, f"{name} left")

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
    if body.names in [p.name for p in room.players.values()]:
            raise HTTPException(status_code=404, detail="Name already taken")
    

    player_id = uuid.uuid4().hex[:8]
    room.add_player(Player(body.name, player_id))

    return {"room_code": room_code, "player_id": player_id}