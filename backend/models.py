class Player:
   
    def __init__(self, name, player_id,):
        self.name = name
        self.id = player_id
        self.is_alive = True


    def eliminate(self):
        self.is_alive = False


class Room:

    def __init__(self, room_code):

        self.room_code = room_code
        self.players = {}
        self.current_letters = None
        self.current_turn = None
        self.is_started = False
        self.is_over = False

    def add_player(self, player):                        #here player.id is key and player is the value 
        self.players[player.id] = player
    
# room = Room("XY12")
# p1 = Player("Alex", 1)                                 #testing the logic 
# room.add_player(p1)
# print(room.players)
# print(room.players[1].name)


   
        
        




        


     
