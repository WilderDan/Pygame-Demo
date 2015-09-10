import pygame # for Rect
import ConfigParser
from events import *

TILE_WIDTH = 50
TILE_HEIGHT = 50

NUM_TILES_WIDE = 22
NUM_TILES_TALL = 13

class GameModel:
    STATE_PREPARING = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2

    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener( self )

        self.player = Player(self.evManager)
        self.current_map = None
        self.state = GameModel.STATE_PREPARING
        
    def Notify(self, event):
    #--------------------------------------------------------------------------
        if isinstance( event, TickEvent ):

	    if self.state == GameModel.STATE_PREPARING:
	        self.Start()

            elif self.state == GameModel.STATE_PAUSED:
                pass 

            else:        
                self.player.character.UpdateLocation()
    #--------------------------------------------------------------------------
        
    def Start(self):
        self.current_map = MapScreen(self.evManager, 'maps/map.txt')
        self.player.character = Character(self.evManager, Player.CHARACTER_START_POINT,\
                                          Player.CHARACTER_MASTER_IMAGE, self.current_map)
        self.state = GameModel.STATE_RUNNING

#------------------------------------------------------------------------------
class Player:
    
    CHARACTER_START_POINT = [ 310, 455 ] 
    CHARACTER_MASTER_IMAGE = 'images/soldier50.bmp'

    def __init__(self, evManager):
        self.evManager = evManager 
        self.evManager.RegisterListener( self )

        self.character = None 

    def Notify(self, event):

        if isinstance( event, PlayerCharMoveRequest ): 
            self.character.directionFacing = event.direction
            self.character.SpeedUp(event.direction)
            
        elif isinstance( event, PlayerCharStop ):
            self.character.StopSpeed(event.direction)

        elif isinstance( event, ShiftPressed ):
            self.character.FlipDirection()
            self.character.backMovementActive = True 
            
        elif isinstance( event, ShiftReleased ):
            self.character.backMovementActive = False
           
#------------------------------------------------------------------------------
class Character:
# GENERIC Character - player character, npc, enemy
# Future reference if becomes imporant... as is even if character isn't moving
# they technically still have a speed associated
   
  #Probably will change to allow different characters to have different speed
    SPEED_MAGNITUDE = 3.0
        # Positive: Down or Right
        # Negative: Up   or Left
 
    #--------------------------------------------------------------------------
    def __init__(self, evManager, location, masterImage, mapData):

        self.evManager = evManager

        self.rect = pygame.Rect( location, (TILE_WIDTH, TILE_HEIGHT) )
        
        self.mapData = mapData
        self.masterImage = masterImage
        self.backMovementActive = False
        self.directionFacing = 'down'
        self.speed = [0,0]
            # self.speed[0] -> horizontal speed
            # self.speed[1] -> vertical speed
        
        ev = CharacterPlacementEvent(self)
        self.evManager.Post( ev )

    #--------------------------------------------------------------------------
    def SpeedUp(self, direction):
        # Note the minus signs

        if direction == 'down':
            self.speed[1] = Character.SPEED_MAGNITUDE

        elif direction == 'up':
            self.speed[1] = -Character.SPEED_MAGNITUDE 

        elif direction == 'left':
            self.speed[0] = -Character.SPEED_MAGNITUDE

        elif direction == 'right':
            self.speed[0] = Character.SPEED_MAGNITUDE

    #--------------------------------------------------------------------------
    def StopSpeed(self, direction):
       
        if direction == 'down' and \
            self.speed[1] > 0:
                self.speed[1] = 0

        elif direction == 'up' and \
            self.speed[1] < 0:
                self.speed[1] = 0

        elif direction == 'left' and \
            self.speed[0] < 0:
                self.speed[0] = 0

        elif direction == 'right' and \
            self.speed[0] > 0:
                self.speed[0] = 0
    #--------------------------------------------------------------------------
    def FlipDirection(self):
        if self.directionFacing == 'up':
            self.directionFacing = 'down'

        elif self.directionFacing == 'down':
            self.directionFacing = 'up'

        elif self.directionFacing == 'left':
            self.directionFacing = 'right'

        elif self.directionFacing == 'right':
            self.directionFacing = 'left'
    #--------------------------------------------------------------------------
    def UpdateLocation(self):
        dx = self.speed[0]
        dy = self.speed[1]

        if dx != 0:
            self.move_single_axis(dx, 0)
        if dy != 0:
            self.move_single_axis(0, dy)
 
        #self.rect.left += self.speed[0]
        #self.rect.top += self.speed[1]

        # Prevent from going off screen
        if self.rect.right > self.mapData.rect.right:
            self.rect.right = self.mapData.rect.right
            self.speed[0] = 0
        if self.rect.left < self.mapData.rect.left:
            self.rect.left = self.mapData.rect.left
            self.speed[0] = 0
        if self.rect.top < self.mapData.rect.top:
            self.rect.top = self.mapData.rect.top
            self.speed[1] = 0
        if self.rect.bottom > self.mapData.rect.bottom:
            self.rect.bottom = self.mapData.rect.bottom
            self.speed[1] = 0
    #--------------------------------------------------------------------------
    def move_single_axis(self, dx, dy):
        # Move the rect
        self.rect.x += dx
        self.rect.y += dy

        # If you collide with a wall, move out based on velocity
        for wall in self.mapData.walls:
            if self.rect.colliderect(wall):
                if dx > 0: # Moving right; Hit the left side of the wall
                    self.rect.right = wall.left
                if dx < 0: # Moving left; Hit the right side of the wall
                    self.rect.left = wall.right
                if dy > 0: # Moving down; Hit the top side of the wall
                    self.rect.bottom = wall.top
                if dy < 0: # Moving up; Hit the bottom side of the wall
                    self.rect.top = wall.bottom
        
#------------------------------------------------------------------------------
class MapScreen:
    # Will I have to delete map screen when going to new map screen?
    STATE_PREPARING = 0
    STATE_LOADED = 1
    #--------------------------------------------------------------------------
    def __init__(self, evManager, filename):
        self.evManager = evManager
        # MapScreen is not a registered listener
        # Can only post events

        self.state = MapScreen.STATE_PREPARING 
        self.struct_back_layer = []
        self.tileset_back_layer = ''
        self.key = {}     # Dictionary of Dictionaries
        self.ascii_walls = [] # list of the ASCII chars that represent a wall
        self.walls = []       # list of Rect 

        screen_width =  TILE_WIDTH * NUM_TILES_WIDE
        screen_height = TILE_HEIGHT * NUM_TILES_TALL
        self.rect = pygame.Rect( (0,0) ,(screen_width, screen_height))

        self.load_map(filename)

    #-------------------------------------------------------------------------- 
    def load_map(self, filename):
        parser = ConfigParser.ConfigParser()
        parser.read(filename)

        self.tileset_back_layer = parser.get("back_layer", "tileset")
        self.struct_back_layer = parser.get("back_layer", "structure").split("\n")

        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc

                # Keep track of which ascii chars are walls
                if parser.has_option(section, 'wall'):
                    self.ascii_walls.append(section)
                    
        self.createWalls()

        self.state = MapScreen.STATE_LOADED

        ev = MapLoadedEvent(self)
	self.evManager.Post( ev )

    #--------------------------------------------------------------------------
    def createWalls(self):
        back_map = self.struct_back_layer
          
        for row in range(len(back_map)):
            for col in range(len(back_map[row])):
                ascii_char = back_map[row][col] 

                if ascii_char in self.ascii_walls:

                    top = row * TILE_HEIGHT
                    left = col * TILE_WIDTH

                    newWall = pygame.Rect( (left, top), (TILE_WIDTH, TILE_HEIGHT))
                    self.walls.append(newWall)
    #--------------------------------------------------------------------------
    def get_dict_back_layer(self, row, col): 
        try:
            char = self.struct_back_layer[row][col]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}

