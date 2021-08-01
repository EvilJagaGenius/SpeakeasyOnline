# Oooooh, what to do here... The goal is to make a Python/Pygame Speakeasy client.  We don't need much, just a deck of cards, a text display, and a tap/untap button.
import pygame, sys, socket, server
pygame.init()

cardSize = (71, 96)
gap = 4

def txtToSurface(startSurface, txt, font, color): # This function covers a pygame.Surface with text.
    surface = startSurface.copy()
    xLimit = surface.get_width()
    yLimit = surface.get_height()
    spaceLength = font.size(' ')[0]
    x = spaceLength
    y = 0
    fontHeight = font.get_height()
    
    ignoreLine = False

    txt = txt.split(' ') # txt is now a list.

    # NTS, have newlines as their own word.
    for word in txt:
        if word == '\n': # If there's a newline char
            if (y + fontHeight * 2 + 4) < yLimit: # Skip a line!
                y += fontHeight + 2
                x = spaceLength
            else:
                break
        else: # For any other word
            if x + font.size(word)[0] <= xLimit: # If the word fits on the surface
                surface.blit(font.render(word, True, color), (x, y)) # Blit it on there
                x += font.size(word)[0]
                if word.endswith('.') or word.endswith('!') or word.endswith('?'): # If it ends with a period or similar thingus
                    x += spaceLength * 2 # Add a double space
                else: # Otherwise
                    x += spaceLength # Add a single space
            else: # BUT if it doesn't fit...
                if (y + fontHeight * 2 + 4) < yLimit: # Skip a line!
                    y += fontHeight + 2
                    x = spaceLength
                    surface.blit(font.render(word, True, color), (x, y)) # Blit it on there
                    x += font.size(word)[0]
                    if word.endswith('.') or word.endswith('!') or word.endswith('?'): # If it ends with a period
                        x += spaceLength * 2 # Add a double space
                    else: # Otherwise
                        x += spaceLength # Add a single space
                else:
                    break

    return surface # Et voila, a text-covered surface!

class Player:
    def __init__(self):
        self.name = "Player"
        self.hand = []
        self.field = []
        self.customers = []
        self.reputation = 1
        self.cash = 0
        self.booze = 0
        self.info = 0
    
class Card:
    def __init__(self, name):
        self.name = name
        self.smallSprite = None
        self.bigSprite = None
        self.text = ""
        self.tapped = False

        self.load()
        
    def load(self):
        self.smallSprite = pygame.image.load("Data\\CardsSmall\\" + self.name + ".png").convert()
        self.smallSprite.set_colorkey(self.smallSprite.get_at((0,0)))
        file = open("Data\\CardText\\" + self.name[0:-1] + ".txt", 'r')
        for line in file:
            self.text += line.strip()
            self.text += ' \n '
        

class Table:
    def __init__(self):
        self.players = []
        self.discardPile = []
        self.serverSocket = None
        self.server = None
        self.hosting = False
        self.turn = 0
        self.localPlayerIndex = -1
        self.localPlayer = Player()
        self.ready = False
        self.chatlog = []
        self.cardsInDeck = 52

    def playGame(self):
        clicked = False
        dragging = False
        selectedCard = False
        mousePos = (-1, -1)
        doubleClickTimer = 0
        
        customersButton = pygame.Rect(0, 0, 100, 100)
        discardButton = pygame.Rect(0, 100, 100, 100)
        drawButton = pygame.Rect(0, 200, 100, 100)
        readyButton = pygame.Rect(0, 300, 100, 100)
        cashButton = pygame.Rect(0, 400, 100, 50)
        boozeButton = pygame.Rect(0, 450, 100, 50)
        infoButton = pygame.Rect(0, 500, 100, 50)
        repButton = pygame.Rect(0, 550, 100, 50)
        fieldRect = pygame.Rect(0,0,0,0)
        textInputBox = pygame.Rect(0, 0, 400, 100)
        textInputString = ""
        textInputType = None
        textInputPrompt = ""
        cardTextSurface = pygame.Surface((400, 800))
        

        if self.hosting:
            ADDRESS = "localhost"
            self.server = server.Server()

        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.connect((ADDRESS, PORT))
        self.serverSocket.setblocking(False)
        # Need to send the server our name next (load this from a file)
        self.localPlayer.name = PLAYERNAME
        self.serverSocket.sendall(bytes("name:" + PLAYERNAME, "utf-8"))
        
        while True:
            #print("Table.playGame() loop")
            if self.hosting:
                self.server.tick()
            #print("Past tick()")
                
            # Mostly rendering code
            WINDOW.fill((0, 127, 0))
            for playerIndex in range(len(self.players)):
                player = self.players[playerIndex]
                if player != None:
                    if playerIndex == self.localPlayerIndex:
                        fieldRect = pygame.Rect(100, (playerIndex*200)+100, WX-100, 200)
                    x = 200
                    y = playerIndex * 200
                    # Draw the player's rect and stats
                    pygame.draw.rect(WINDOW, WHITE, pygame.Rect(100, y, WX-100, 200), 1)
                    WINDOW.blit(FONT.render(player.name, True, WHITE), (100, y))
                    # Draw their cards in hand and on the field
                    for card in player.hand:
                        cardRect = pygame.Rect(x, y, cardSize[0], cardSize[1])
                        if cardRect.collidepoint(mousePos):
                            if clicked and playerIndex == self.localPlayerIndex:
                                selectedCard = card
                            cardTextSurface.fill((0,0,0))
                            WINDOW.blit(txtToSurface(cardTextSurface, card.text, FONT, WHITE), (WX//2, WY//2))
                        if dragging and selectedCard == card:
                            cardRect.center = mousePos
                        if playerIndex == self.localPlayerIndex:
                            WINDOW.blit(card.smallSprite, cardRect)
                        else:
                            WINDOW.blit(CARDBACK, cardRect)
                        x += cardRect.width + gap
                    x = 200
                    y = (playerIndex * 200) + 100
                    for card in player.field:
                        cardRect = pygame.Rect(x, y, cardSize[0], cardSize[1])
                        sprite = card.smallSprite
                        if card.tapped:
                            cardRect = pygame.Rect(x, y, cardSize[1], cardSize[0])
                            sprite = pygame.transform.rotate(card.smallSprite, 90)
                        if clicked and cardRect.collidepoint(mousePos) and playerIndex == self.localPlayerIndex:
                            selectedCard = card
                            if doubleClickTimer > 0:
                                print("Tapping", card.name)
                                self.serverSocket.sendall(bytes("tap:" + card.name, "utf-8"))
                            doubleClickTimer = 500
                        if dragging and selectedCard == card:
                            cardRect.center = mousePos
                        WINDOW.blit(sprite, cardRect)
                        x += cardRect.width + gap

            # Render the side buttons
            WINDOW.blit(FONT.render("Customers: " + str(len(self.localPlayer.customers)), True, WHITE), customersButton)
            pygame.draw.rect(WINDOW, WHITE, customersButton, 1)
            WINDOW.blit(FONT.render("Discard", True, WHITE), discardButton)
            pygame.draw.rect(WINDOW, WHITE, discardButton, 1)
            WINDOW.blit(FONT.render("Draw: " + str(self.cardsInDeck), True, WHITE), drawButton)
            pygame.draw.rect(WINDOW, WHITE, drawButton, 1)
            WINDOW.blit(FONT.render("Ready", True, WHITE), readyButton)
            pygame.draw.rect(WINDOW, WHITE, readyButton, 1)
            WINDOW.blit(FONT.render("Cash: " + str(self.localPlayer.cash), True, WHITE), cashButton)
            pygame.draw.rect(WINDOW, WHITE, cashButton, 1)
            WINDOW.blit(FONT.render("Booze: " + str(self.localPlayer.booze), True, WHITE), boozeButton)
            pygame.draw.rect(WINDOW, WHITE, boozeButton, 1)
            WINDOW.blit(FONT.render("Info: " + str(self.localPlayer.info), True, WHITE), infoButton)
            pygame.draw.rect(WINDOW, WHITE, infoButton, 1)
            WINDOW.blit(FONT.render("Reputation: " + str(self.localPlayer.reputation), True, WHITE), repButton)
            pygame.draw.rect(WINDOW, WHITE, repButton, 1)

            # Render a box for text input
            if textInputType != None:
                pygame.draw.rect(WINDOW, (0,0,0), textInputBox)
                WINDOW.blit(FONT.render(textInputPrompt, True, WHITE), (textInputBox.left+10, textInputBox.top))
                WINDOW.blit(FONT.render(textInputString, True, WHITE), (textInputBox.left+10, textInputBox.top+50))
                        
            # End rendering code
            # Get user input
            clicked = False
            mousePos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked = True
                    dragging = True
                    if readyButton.collidepoint(mousePos):
                        self.serverSocket.sendall(b"ready:")
                    elif drawButton.collidepoint(mousePos):
                        if event.button == 1:
                            self.serverSocket.sendall(bytes("draw:", "utf-8"))
                        elif event.button == 3:
                            #searchingFor = input("Search the deck for which card?  ")
                            #self.serverSocket.sendall(bytes("draw:"+searchingFor, "utf-8"))
                            textInputBox.topleft = drawButton.topleft
                            textInputType = "draw"
                            textInputPrompt = "Search the deck for which card?"
                            textInputString = ""
                    elif cashButton.collidepoint(mousePos):
                        if event.button == 1:
                            self.localPlayer.cash += 1
                        elif event.button == 3:
                            self.localPlayer.cash -= 1
                        self.serverSocket.sendall(bytes("setCash:" + str(self.localPlayer.cash), "utf-8"))
                    elif boozeButton.collidepoint(mousePos):
                        if event.button == 1:
                            self.localPlayer.booze += 1
                        elif event.button == 3:
                            self.localPlayer.booze -= 1
                        self.serverSocket.sendall(bytes("setBooze:" + str(self.localPlayer.booze), "utf-8"))
                    if infoButton.collidepoint(mousePos):
                        if event.button == 1:
                            self.localPlayer.info += 1
                        elif event.button == 3:
                            self.localPlayer.info -= 1
                        self.serverSocket.sendall(bytes("setInfo:" + str(self.localPlayer.info), "utf-8"))
                    if repButton.collidepoint(mousePos):
                        if event.button == 1:
                            self.localPlayer.reputation += 1
                        elif event.button == 3:
                            self.localPlayer.reputation -= 1
                        self.serverSocket.sendall(bytes("setRep:" + str(self.localPlayer.reputation), "utf-8"))
                if event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                    if selectedCard != None:
                        if customersButton.collidepoint(mousePos):
                            self.serverSocket.sendall(bytes("customer:" + selectedCard.name, "utf-8"))
                        elif discardButton.collidepoint(mousePos):
                            self.serverSocket.sendall(bytes("discard:" + selectedCard.name, "utf-8"))
                        elif drawButton.collidepoint(mousePos):
                            self.serverSocket.sendall(bytes("shuffleIn:" + selectedCard.name, "utf-8"))
                        elif fieldRect.collidepoint(mousePos) and selectedCard in player.hand:
                            self.serverSocket.sendall(bytes("play:" + selectedCard.name, "utf-8"))

                    selectedCard = None

                # Text box input
                elif event.type == pygame.KEYDOWN:
                    if textInputType != None:
                        if event.key == pygame.K_RETURN:
                            if textInputType == "draw":
                                self.serverSocket.sendall(bytes("draw:"+textInputString.upper(), "utf-8"))
                            textInputType = None
                            textInputString = ""
                            textInputPrompt = ""
                        elif event.key == pygame.K_BACKSPACE:
                            if len(textInputString) > 0:
                                textInputString = textInputString[0:-1]
                        elif event.key == pygame.K_ESCAPE:
                            textInputType = None
                            textInputString = ""
                            textInputPrompt = ""
                        else:
                            textInputString += pygame.key.name(event.key).upper()

            if doubleClickTimer > 0:
                doubleClickTimer -= CHRONO.get_time()
            # Get data from the server
            try:
                data = str(self.serverSocket.recv(1024), "utf-8")
                if (data):
                    commands = data.split("\n")
                    for command in commands:
                        if len(command) > 0:
                            self.takeCommand(command)
            except BlockingIOError:
                pass

            pygame.display.update()
            CHRONO.tick()  # No framerate cap, it's not needed

    def takeCommand(self, command):
        print("Client command:", command)
        splitCommand = command.split(":")
        if command.startswith("addPlayer:"):  # addPlayer:index:name
            index = int(splitCommand[1])
            while index >= len(self.players):
                self.players.append(None)
            if index != self.localPlayerIndex:
                self.players[index] = Player()
                self.players[index].name = splitCommand[2]
        elif command.startswith("playerIndex:"):  # playerIndex:index
            print("Changing self.localPlayerIndex")
            self.localPlayerIndex = int(splitCommand[1])
            while self.localPlayerIndex >= len(self.players):
                self.players.append(None)
            self.players[self.localPlayerIndex] = self.localPlayer
        elif command.startswith("draw:"):  # draw:player:card
            self.players[int(splitCommand[1])].hand.append(Card(splitCommand[2]))
            self.cardsInDeck -= 1
        elif command.startswith("play:"):  # play:player:card
            player = self.players[int(splitCommand[1])]
            for card in player.hand:
                if card.name == splitCommand[2]:
                    player.field.append(card)
                    player.hand.remove(card)
        elif command.startswith("tap:"):  # tap:player:card
            player = self.players[int(splitCommand[1])]
            for card in player.field:
                if card.name == splitCommand[2]:
                    card.tapped = not card.tapped
                    break
        elif command.startswith("untap"):
            for card in self.players[int(splitCommand[1])].field:
                card.tapped = False
        elif command.startswith("setRep:"):
            self.players[int(splitCommand[1])].reputation = int(splitCommand[2])
        elif command.startswith("setCash:"):
            self.players[int(splitCommand[1])].cash = int(splitCommand[2])
        elif command.startswith("setBooze:"):
            self.players[int(splitCommand[1])].booze = int(splitCommand[2])
        elif command.startswith("setInfo:"):
            self.players[int(splitCommand[1])].info = int(splitCommand[2])
        elif command.startswith("startTurn:"):  # startTurn:player
            self.turn = int(splitCommand[1])
        elif command.startswith("chat:"):  # chat:player:message
            self.chatlog.insert(0, self.players[int(splitCommand[1])].name + splitCommand[2])
        elif command.startswith("discard"):
            player = self.players[int(splitCommand[1])]
            for card in player.field:
                if card.name == splitCommand[2]:
                    self.discardPile.append(card)
                    player.field.remove(card)
                    break
            for card in player.hand:
                if card.name == splitCommand[2]:
                    self.discardPile.append(card)
                    player.hand.remove(card)
        elif command.startswith("customer:"):
            player = self.players[int(splitCommand[1])]
            for card in player.field:
                if card.name == splitCommand[2]:
                    player.customers.append(card)
                    player.field.remove(card)
                    break
            for card in player.hand:
                if card.name == splitCommand[2]:
                    player.customers.append(card)
                    player.hand.remove(card)
        elif command.startswith("shuffleIn:"):
            player = self.players[int(splitCommand[1])]
            for card in player.field:
                if card.name == splitCommand[2]:
                    player.field.remove(card)
                    break
            for card in player.hand:
                if card.name == splitCommand[2]:
                    player.hand.remove(card)
                    break
            self.cardsInDeck += 1
"""
TABLE = Table()
TABLE.hosting = True
TABLE.playGame()
"""
PLAYERNAME = input("Enter your name:  ")
print("Choose an option:\n1) Host a game\n2) Connect to a game\nAnything else to exit")
choice = input()

PORT = 1920
ADDRESS = "localhost"
WX = 1600
WY = 900
WINDOW = pygame.display.set_mode((WX, WY), 0, 32)
pygame.display.set_caption("Speakeasy Tabletop")
FONT = pygame.font.Font(None, 22)
WHITE = (255,255,255)
CHRONO = pygame.time.Clock()
CARDBACK = pygame.image.load("Data\\CardsSmall\\Back.png").convert()
CARDBACK.set_colorkey(CARDBACK.get_at((0,0)))

if choice == '1':
    TABLE = Table()
    TABLE.hosting = True
    TABLE.playGame()
elif choice == '2':
    TABLE = Table()
    ADDRESS = input("Enter the server's IP address:  ")
    TABLE.playGame()
# Anything else jumps to here
print("Exiting...")

