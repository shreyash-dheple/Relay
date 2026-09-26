class Player:
   
    def __init__(self, name, player_id,):
        self.name = name
        self.id = player_id
        self.is_alive = True


    def eliminate(self):
        self.is_alive = False


class Room:

    def __init__(self, room_code):
        self.room_code = room_code == "XY"
        self.players = {}
        self.starting_letter = "SH"

    def add_player(self, player):
        self.players[player.player_id] = {
            
        }
       
room = Room("XY")
Player = room.add_player(77)
print(Room.players)
       
    
   
        
        




        


     
