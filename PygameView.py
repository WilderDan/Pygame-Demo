import pygame
from events import *

from GameModel import TILE_WIDTH, \
                      TILE_HEIGHT, \
                      NUM_TILES_WIDE, \
                      NUM_TILES_TALL

SCREEN_WIDTH =  TILE_WIDTH * NUM_TILES_WIDE
SCREEN_HEIGHT = TILE_HEIGHT * NUM_TILES_TALL

#------------------------------------------------------------------------------ 
class PygameView:
    # Be responsible for screen shifts!!!!
       
    def __init__(self, evManager):
        self.evManager = evManager
	self.evManager.RegisterListener( self )

	pygame.init()
	self.window = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )

        img_icon = pygame.image.load("images/img_icon.bmp")
        pygame.display.set_icon(img_icon)  
	pygame.display.set_caption( 'Demo RPG' )

	self.background = pygame.Surface( self.window.get_size() )
        self.screenRect = self.background.get_rect()
	self.background.fill( (0,0,255) ) # Blue
	self.window.blit( self.background, (0,0) )
        
        self.backSprites = pygame.sprite.RenderUpdates()
        self.charSprites = pygame.sprite.RenderUpdates()

	pygame.display.update()

    #--------------------------------------------------------------------------
    def Notify(self, event):
        if isinstance( event, TickEvent ):
            self.backSprites.clear( self.window, self.background )

	    self.charSprites.update()

	    dirtyRects1 = self.backSprites.draw( self.window )
            dirtyRects2 = self.charSprites.draw( self.window )

            dirtyRects = dirtyRects1 + dirtyRects2
			
	    pygame.display.update( dirtyRects )

        elif isinstance( event, MapLoadedEvent ):
            self.CreateMapTiles(event.map_screen)

        elif isinstance( event, CharacterPlacementEvent ):
            self.ShowCharacter(event.character) 

    #--------------------------------------------------------------------------
    def CreateMapTiles(self, map_screen):
        # delete exisiting sprites?
    
        back_map = map_screen.struct_back_layer
        tileset = map_screen.tileset_back_layer
        file_path = "images/" + tileset
 
        for row in range(len(back_map)):
            for col in range(len(back_map[row])):

                char_map = map_screen.get_dict_back_layer(row, col)

                #char_map is a dictionary containing the 'item : value' entries 
                #of the sections defined by the character at position: row, col
                #in the back_layer

                tile_xcoord = int(char_map['tile_xcoord'])
                tile_ycoord = int(char_map['tile_ycoord'])
                
                image = self.GetTileImage(file_path, tile_xcoord, tile_ycoord)
                newTile = TileSprite(image, row, col, self.backSprites)

    #--------------------------------------------------------------------------
    def GetTileImage(self, image_file, row, col):
        image = pygame.image.load(image_file)
 
        left = col * TILE_WIDTH
        top = row * TILE_HEIGHT
 
        rect = pygame.Rect(left, top, TILE_WIDTH, TILE_HEIGHT)
        tile_image = image.subsurface(rect)

        return tile_image

    #--------------------------------------------------------------------------
    def ShowCharacter(self, character):
        characterSprite = CharacterSprite(character, character.masterImage, \
                                          self.screenRect, self.charSprites)
	characterSprite.rect.top = character.rect.top
        characterSprite.rect.left = character.rect.left     

#------------------------------------------------------------------------------
class TileSprite(pygame.sprite.Sprite):

    def __init__(self, image, row, col, group = None):
        pygame.sprite.Sprite.__init__(self, group)

        self.image  = image
        self.rect   = self.image.get_rect()
        self.rect.top = row * TILE_HEIGHT
        self.rect.left = col * TILE_WIDTH

#------------------------------------------------------------------------------
class CharacterSprite(pygame.sprite.DirtySprite):
    
    #--------------------------------------------------------------------------
    def __init__(self, character, image, screenRect, group = None):
        pygame.sprite.Sprite.__init__(self, group)

        self.character = character # From game model

        self.masterImage = pygame.image.load(image)
        self.masterImage.convert()
        self.masterImage.set_colorkey( (255, 255, 255) )

        self.screenRect = screenRect
         
        self.downImages = []
        self.upImages = []
        self.leftImages = []
        self.rightImages = []

        self.imageDirection = []
        
        self.frameSize = (TILE_WIDTH, TILE_HEIGHT) 
        self.frame = 0

        # Variables for animation
        self.pause = 0
        
        #-----Create list of images for each direction-------------------------
        for row in range(4):
            for col in range(2):
               if row == 0:
                   position = (col * self.frameSize[1], 0 )
                   image = self.masterImage.subsurface( position , self.frameSize )
                   self.downImages.append(image)
               elif row == 1:
                   position = (col * self.frameSize[1], self.frameSize[0] )
                   image = self.masterImage.subsurface( position , self.frameSize )
                   self.upImages.append(image)
               elif row == 2: 
                   position = (col * self.frameSize[1], 2 * self.frameSize[0] )
                   image = self.masterImage.subsurface( position , self.frameSize )
                   self.leftImages.append(image)
               elif row == 3: 
                   position = (col * self.frameSize[1], 3 * self.frameSize[0] )
                   image = self.masterImage.subsurface( position , self.frameSize )
                   self.rightImages.append(image)
        #----------------------------------------------------------------------

        self.imageDirection = self.downImages
        self.image = self.imageDirection[self.frame]
        self.rect = self.image.get_rect()
 
    #--------------------------------------------------------------------------
    def update(self):
        # Decide image directions
        if self.character.directionFacing == 'up':
            self.imageDirection = self.upImages
 
        elif self.character.directionFacing == 'down':
            self.imageDirection = self.downImages

        elif self.character.directionFacing == 'left':
            self.imageDirection = self.leftImages

        elif self.character.directionFacing == 'right':
            self.imageDirection = self.rightImages
 
        # Remember sprite's previous position
        oldRect = self.rect.copy()

        # Get new position from character data
        self.rect.top = self.character.rect.top
        self.rect.left = self.character.rect.left

        dx = self.character.speed[0]
        dy = self.character.speed[1]

        # Check collisions on each axis separately
        if dx != 0:
            self.CollideAxis(dx, 0)
        if dy != 0:
            self.CollideAxis(0, dy)

        if self.rect != oldRect:
            self.Animation()

        else: 
            self.image = self.imageDirection[0]

    def CollideAxis(self, dx, dy):
        # If collision fix position
        if self.screenRect.contains(self.rect) == False:
            if dx > 0: # Moving right; Hit the left side of the wall
                self.rect.right = self.screenRect.left
                #self.character.location[0] = self.rect.left
            if dx < 0: # Moving left; Hit the right side of the wall
                self.rect.left = self.screenRect.right
                #self.character.location[0] = self.rect.left
            if dy > 0: # Moving down; Hit the top side of the wall
                self.rect.bottom = self.screenRect.top
                #self.character.location[1] = self.rect.top
            if dy < 0: # Moving up; Hit the bottom side of the wall
                self.rect.top = self.screenRect.bottom
                #self.character.location[1] = self.rect.top


    #--------------------------------------------------------------------------
    def Animation(self):

      # Determine image direction based on character speed:

        if self.character.speed[1] > 0:  # Moving down
            if self.character.backMovementActive == False:
                self.imageDirection = self.downImages
            else: 
                self.imageDirection = self.upImages

        elif self.character.speed[1] < 0: # Moving up
            if self.character.backMovementActive == False:
                self.imageDirection = self.upImages
            else: 
                self.imageDirection = self.downImages

        elif self.character.speed[0] < 0: # Moving left
            if self.character.backMovementActive == False:
                self.imageDirection = self.leftImages
            else:
                self.imageDirection = self.rightImages

        elif self.character.speed[0] > 0: # Moving right
            if self.character.backMovementActive == False:
                self.imageDirection = self.rightImages
            else:
                self.imageDirection = self.leftImages
        
        #----------------------------------------------------------------------
        delay = 10       
            
        self.pause += 1
        if self.pause >= delay:
            self.pause = 0
            self.frame += 1
            if self.frame >= len(self.imageDirection):
                self.frame = 0               
            
            self.image = self.imageDirection[self.frame]
