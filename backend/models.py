import random

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
        self.words = set()
        self.used_words = set()


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

                 
    def check_word(self, word):
        word = word.lower()
        """Return True if word starts with the room's current letters (case-insensitive)."""
        return word.startswith(self.current_letters.lower()) and word in self.words and word not in self.used_words


    def start_round(self, words):
        self.words = words
        word_list = list(words)
        current_word = random.choice(word_list)
        self.current_letters = pick_letters(current_word)
        self.used_words = set()


    def submit_word(self, word):
        if self.check_word(word):                               #the self.check_word() returns Boolean 
            self.used_words.add(word)
            self.next_turn()
        else:
            current_player = self.players[self.current_turn]
            current_player.eliminate()
            self.next_turn()
            

def load_word(filename):
        """Load words from filename into a set of lowercase words."""
        words = set()
        with open(filename, "r") as file:
            for line in file:
                word = line.strip().lower()
                words.add(word)
        return words


def pick_letters(word):
    """Decide how many starting letters to reveal based on word length."""
    if len(word) <= 4:
        n = 2
    elif len(word) <= 7:
        n = 3
    else:
        n = 4
    return word[0:n]
