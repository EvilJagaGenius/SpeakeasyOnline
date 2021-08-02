# Speakeasy server.
import socket, random
PORT = 1920

class Player:
    def __init__(self):
        self.name = "Player"
        self.ready = False
        self.hand = []
        self.field = []
        self.customers = []
        self.reputation = 1
        self.cash = 0
        self.booze = 0
        self.info = 0
        self.socket = None

class Card:
    def __init__(self, name):
        self.name = name
        self.tapped = False

class Server:
    def __init__(self):
        self.players = []
        self.deck = []
        self.discardPile = []
        self.createDeck()
        self.turn = 0
        self.gameStarted = False

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(('', PORT))
        self.listener.listen()
        self.listener.setblocking(False)

    def createDeck(self):
        self.deck.clear()
        ranks = ['K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A']
        suits = ['S', 'C', 'H', 'D']
        for rank in ranks:
            for suit in suits:
                self.deck.append(Card(rank+suit))
        random.shuffle(self.deck)
    
    def tick(self):
        try:
            conn, addr = self.listener.accept()
            # Create a new player if one connected
            newPlayer = Player()
            newPlayer.socket = conn
            self.players.append(newPlayer)
            conn.sendall(bytes("playerIndex:" + str(len(self.players)-1), "utf-8"))
        except BlockingIOError:
            pass
        # Get input from the players
        for i in range(len(self.players)):
            try:
                player = self.players[i]
                data = str(player.socket.recv(1024), "utf-8")
                splitData = data.split(":")
                print("Server command:", data)
                if data.startswith("name:"):
                    player.name = splitData[1]
                    self.broadcast("addPlayer:" + str(i) + ":" + player.name)
                elif data.startswith("ready:"):
                    player.ready = True
                    if self.allReady() and not self.gameStarted:  # Start the game
                        self.startGame()
                        starter = random.randint(1, len(self.players)) - 1
                        self.broadcast("startTurn:" + str(starter))
                elif data.startswith("draw:"):
                    #print(len(splitData))
                    if len(splitData[1]) == 0 and len(self.deck) > 0:  # No card specified, pick a random card
                        card = self.deck.pop()
                        player.hand.append(card)
                        self.broadcast("draw:" + str(i) + ":" + card.name)
                    else:  # Search the deck for a specific card
                        for card in self.deck:
                            if card.name == splitData[1]:
                                self.broadcast("draw:" + str(i) + ":" + card.name)
                                player.hand.append(card)
                                self.deck.remove(card)
                                random.shuffle(self.deck)  # Shuffle the deck afterwards
                                break
                elif data.startswith("play:"):
                    for card in player.hand:
                        if card.name == splitData[1]:
                            player.field.append(card)
                            player.hand.remove(card)
                            self.broadcast("play:" + str(i) + ":" + splitData[1])
                            break
                elif data.startswith("tap:"):
                    for card in player.field:
                        if card.name == splitData[1]:
                            card.tapped = not card.tapped
                            self.broadcast("tap:" + str(i) + ":" + splitData[1])
                elif data.startswith("untap:"):
                    for card in player.field:
                        card.tapped = False
                    self.broadcast("untap:" + str(i))
                elif data.startswith("setRep:"):
                    player.reputation = int(splitData[1])
                    self.broadcast("setRep:" + str(i) + ":" + str(player.reputation))
                elif data.startswith("setCash:"):
                    player.cash = int(splitData[1])
                    self.broadcast("setCash:" + str(i) + ":" + str(player.cash))
                elif data.startswith("setBooze:"):
                    player.booze = int(splitData[1])
                    self.broadcast("setBooze:" + str(i) + ":" + str(player.booze))
                elif data.startswith("setInfo:"):
                    player.info = int(splitData[1])
                    self.broadcast("setInfo:" + str(i) + ":" + str(player.info))
                elif data.startswith("pass:"):
                    self.turn += 1
                    self.turn = self.turn % len(self.players)
                    self.broadcast("startTurn:" + str(self.turn))
                elif data.startswith("discard"):
                    for card in player.field:
                        if card.name == splitData[1]:
                            self.discardPile.append(card)
                            player.field.remove(card)
                            break
                    for card in player.hand:
                        if card.name == splitData[1]:
                            self.discardPile.append(card)
                            player.hand.remove(card)
                    self.broadcast("discard:" + str(i) + ":" + splitData[1])
                elif data.startswith("customer:"):
                    for card in player.field:
                        if card.name == splitData[1]:
                            player.customers.append(card)
                            player.field.remove(card)
                            break
                    for card in player.hand:
                        if card.name == splitData[1]:
                            player.customers.append(card)
                            player.hand.remove(card)
                            break
                    self.broadcast("customer:" + str(i) + ":" + splitData[1])
                elif data.startswith("shuffleIn:"):
                    for card in player.field:
                        if card.name == splitData[1]:
                            self.deck.append(card)
                            player.field.remove(card)
                            break
                    for card in player.hand:
                        if card.name == splitData[1]:
                            self.deck.append(card)
                            player.hand.remove(card)
                            break
                    random.shuffle(self.deck)
                    self.broadcast("shuffleIn:" + str(i) + ":" + splitData[1])
                elif data.startswith("chat:"):
                    self.broadcast("chat:" + str(i) + ":" + splitData[1])
                    
            except BlockingIOError:
                pass

    def broadcast(self, message):
        for player in self.players:
            player.socket.sendall(bytes("\n" + message, "utf-8"))

    def allReady(self):
        for player in self.players:
            if not player.ready:
                return False
        return True

    def startGame(self):
        for i in range(len(self.players)):
            player = self.players[i]
            for j in range(3):
                card = self.deck.pop()
                player.hand.append(card)
                self.broadcast("draw:" + str(i) + ":" + card.name)
            # I suppose we could let people set these themselves
            player.reputation = 1
            self.broadcast("setRep:" + str(i) + ":1")
            player.cash = 2
            self.broadcast("setCash:" + str(i) + ":2")
            player.booze = 1
            self.broadcast("setBooze:" + str(i) + ":1")
            player.info = 1
            self.broadcast("setInfo:" + str(i) + ":1")
        self.gameStarted = True


        

if __name__ == "__main__":
    print("Starting Speakeasy server...")
    server = Server()
    while True:
        server.tick()
