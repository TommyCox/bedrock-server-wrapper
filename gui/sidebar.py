import tkinter
from basegui import GUI
from control_panel import ControlPanel
from player_list import PlayerList

class SideBar(GUI):
    def build_gui(self):
        # Control Panel
        ControlPanel(self).grid(row=0, sticky = self.onAll)
        # Player List
        PlayerList(self).grid(row=1, sticky = self.onAll)

    def layout_config(self):
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 2)

if __name__ == "__main__":
    # Test this module when run directly.
    from basegui import test_gui
    test_gui(__file__, SideBar)