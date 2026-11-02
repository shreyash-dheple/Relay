from game import Player, Room , load_word
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import string
import uuid

app = FastAPI()

rooms = {}
prompt_words = load_word("words.txt")
valid_words = load_word("words_alpha.txt")

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

    player_id = uuid.uuid4().hex[:8]
    room.add_player(Player(body.name, player_id))

    return {"room_code": room_code, "player_id": player_id}