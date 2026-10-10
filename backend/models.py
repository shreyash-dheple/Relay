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

    def next_turn(self):                                           #this is next turn function inside Room class
         x = list(self.players.keys())                             #x is a list of players in the Room
         if self.current_turn is None:
             self.current_turn = x[0]
         else:
             current_position = x.index(self.current_turn)
             for step in range(1, len(x) + 1):
                 candidate_position = (current_position + step) % len(x)
                 candidate_id = x[candidate_position]
                 candidate_player = self.players[candidate_id]
                 if candidate_player.is_alive:
                       self.current_turn = candidate_id
                       break
     
                        
            
        
                  

room = Room("XY12")
p1 = Player("Alex", 1)
p2 = Player("Sam", 2)
p3 = Player("Jordan", 3)
room.add_player(p1)
room.add_player(p2)
room.add_player(p3)

room.next_turn()
print(room.current_turn)   # expect 1

p2.eliminate()              # Sam is out
room.next_turn()
print(room.current_turn)   # expect 3, skipping Sam (2)                                                                           
          
   

    







        


     
