from pygame.time import Clock
from events import TickEvent, QuitEvent

class CPUSpinnerController:
    """    Keeps the program running until notified of a QuitEvent    """

    def __init__(self, evManager):
        self.evManager = evManager
	self.evManager.RegisterListener( self )
     
        self.clock = Clock()

	self.keepGoing = 1

    #----------------------------------------------------------------------
    def Run(self):
        while self.keepGoing:
            self.clock.tick(60)
	    event = TickEvent()
	    self.evManager.Post( event )

    #----------------------------------------------------------------------
    def Notify(self, event):
        if isinstance( event, QuitEvent ):
	    #this will stop the while loop from running
	    self.keepGoing = False

