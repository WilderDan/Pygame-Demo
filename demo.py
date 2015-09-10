import EventManager
import CPUSpinnerController
import GameModel
import PygameView
import KeyboardController

def main():
    """I should put in a real docstring sometime..."""

    evManager  = EventManager.EventManager()

    spinner    = CPUSpinnerController.CPUSpinnerController( evManager )
        
    game       = GameModel.GameModel( evManager )
    pygameView = PygameView.PygameView( evManager )
    keybd      = KeyboardController.KeyboardController( evManager )

    spinner.Run()

if __name__ == "__main__":
   main()
