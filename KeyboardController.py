import pygame
from pygame.locals import * 

from events import *

# Make variables to change control layout!!!
# Left press; Right press; Right release --> Fix

class KeyboardController:
    """    KeyboardController takes Pygame events generated by the
	   keyboard and uses them to control the model, by sending Requests
	   or to control the Pygame display directly, as with the QuitEvent
    """

    def __init__(self, evManager):
        self.evManager = evManager
	self.evManager.RegisterListener( self )

    #--------------------------------------------------------------------------
    def Notify(self, event):
        if isinstance( event, TickEvent ):
	
	    for event in pygame.event.get():
                ev = None

	        if event.type == QUIT:
		        ev = QuitEvent()
				
                elif event.type == KEYDOWN \
                    and event.key == K_ESCAPE:
		        ev = QuitEvent()

		elif event.type == KEYDOWN \
		    and event.key == K_UP:
		        direction = 'up'
			ev = PlayerCharMoveRequest(direction)

		elif event.type == KEYDOWN \
		    and event.key == K_DOWN:
		        direction = 'down'
			ev = PlayerCharMoveRequest(direction)

		elif event.type == KEYDOWN \
		    and event.key == K_LEFT:
		        direction = 'left'
			ev = PlayerCharMoveRequest(direction)

		elif event.type == KEYDOWN \
		    and event.key == K_RIGHT:
		        direction = 'right'
			ev = PlayerCharMoveRequest(direction)

                #------------------------------------------------------

		elif event.type == KEYUP \
		    and event.key == K_UP:
		        direction = 'up'
			ev = PlayerCharStop(direction)

		elif event.type == KEYUP \
		    and event.key == K_DOWN:
		        direction = 'down'
			ev = PlayerCharStop(direction)

		elif event.type == KEYUP \
		    and event.key == K_LEFT:
		        direction = 'left'
			ev = PlayerCharStop(direction)

		elif event.type == KEYUP \
		    and event.key == K_RIGHT:
		        direction = 'right'
			ev = PlayerCharStop(direction)

               #------------------------------------------------------

                elif event.type == KEYDOWN and event.key == K_LSHIFT:
                       ev = ShiftPressed() 

                elif event.type == KEYUP and event.key == K_LSHIFT:
                       ev = ShiftReleased() 
                       
	        if ev:
	            self.evManager.Post( ev )
