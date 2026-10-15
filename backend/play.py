from game import Player, Room, load_word
prompt_words = load_word("words.txt")          
valid_words = load_word("words_alpha.txt")   

room = Room("TEST01")

words = load_word("words_alpha.txt")
room.valid_words = valid_words

p1 = Player(input("Player 1 name: "), 1)
p2 = Player(input("Player 2 name: "), 2)
p3 = Player(input("Player 3 name: "), 3)
room.add_player(p1)
room.add_player(p2)
room.add_player(p3)

room.next_turn()   

while not room.is_game_over():
    room.start_round(prompt_words)   
    current_player = room.players[room.current_turn]
    print(f"\n{current_player.name}'s turn! Starting letters: {room.current_letters}")
    word = input("Enter your word: ")
    room.submit_word(word)

winner = room.get_winner()
print(f"\n{winner.name} wins!")