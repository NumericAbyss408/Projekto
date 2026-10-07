import Core
Core.Setup()

import Gui
def cycle():
	Gui.Render()
	Core.Terminate()
	match Gui.ChosenSM:
		case Gui.ShutdownMode.PENDING_RESTART:
			print("Restarting")
			cycle()
		case Gui.ShutdownMode.PERMANENT_SHUTDOWN:
			print("Shutting Down")



if __name__ == "__main__":
	cycle()
