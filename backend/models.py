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
        self.players = {}                                          #the player dict is in Room class
        self.current_letters = None
        self.current_turn = None
        self.is_started = False
        self.is_over = False

    def add_player(self, player):                                 #here player.id is key and player is the value 
        self.players[player.id] = player

    def next_turn(self):
         x = list(self.players.keys())                             #this is next turn function inside Room class
         print(x)
             
    
    
room = Room("XY12")
p1 = Player("Alex", 1) 
p2 = Player("shreyash", 33)
p3 = Player("prashant", 45)                                  #testing the logic 
room.add_player(p1)
room.add_player(p2)
room.add_player(p3)


Room.next_turn(room)



        


     
