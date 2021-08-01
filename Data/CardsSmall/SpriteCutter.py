# Spritesheet cutter for the Windows XP card set
import pygame, sys
pygame.init()

startPoint = (15, 35)
altStartPoint = (319, 35)
cardSize = (71, 96)
gapSize = (4, 4)
ranks = ['K', 'Q', 'J', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10']
suits = ['S', 'C', 'H', 'D']

mainSheet = pygame.image.load("MainSheet.png")
mainSheet.set_colorkey(mainSheet.get_at((0,0)))

for i in range(13):
    for j in range(4):
        cardImage = mainSheet.subsurface(pygame.Rect((startPoint[0] + (gapSize[0] + cardSize[0]) * j, startPoint[1] + (gapSize[1] + cardSize[1]) * i), cardSize))
        altCardImage = mainSheet.subsurface(pygame.Rect((altStartPoint[0] + (gapSize[0] + cardSize[0]) * j, altStartPoint[1] + (gapSize[1] + cardSize[1]) * i), cardSize))
        pygame.image.save(cardImage, ranks[i] + suits[j] + ".png")
        pygame.image.save(altCardImage, ranks[i] + suits[j] + "alt.png")

pygame.quit()
sys.exit()
        
