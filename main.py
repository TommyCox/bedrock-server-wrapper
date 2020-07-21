# TODO: Add settings using configparser library.
from wrapper_gui import GUI as MakeGUI
gui = MakeGUI()
gui.start_server()
gui.mainloop()