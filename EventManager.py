from events import *

def Debug(message):
    print message

class EventManager:
	"""This object is responsible for coordinating most communication
	between the Model, View, and Controller."""

	def __init__(self):
		from weakref import WeakKeyDictionary
		self.listeners = WeakKeyDictionary()
	
	#----------------------------------------------------------------------
	def RegisterListener( self, listener ):
		self.listeners[ listener ] = 1

	#----------------------------------------------------------------------
	def UnregisterListener( self, listener ):
		if listener in self.listeners:
			del self.listeners[ listener ]

	#----------------------------------------------------------------------
	def Post( self, event ):
		if not isinstance(event, TickEvent):
			Debug( "     Message: " + event.name )
		for listener in self.listeners:
			#NOTE: If the weakref has died, it will be 
			#automatically removed, so we don't have 
			#to worry about it.

			listener.Notify( event )

                        # Consider adding code to decide which listener is notified
                        # of what
