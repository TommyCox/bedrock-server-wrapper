import tkinter
from tkinter.scrolledtext import ScrolledText
from basegui import GUI

class PlayerList(GUI):
    def build_gui(self):
        title2 = tkinter.Label(self, text = "Players")
        title2.grid()

        scrollbox = ScrolledText(self, width = 20, height = 10, state = tkinter.DISABLED)
        scrollbox.grid(row = 1, sticky = self.onAll)
        # self.player_list = scrollbox

    def layout_config(self):
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.configure(padx = 10, pady = 10)



if __name__ == "__main__":
    # Test this module when run directly.
    from basegui import test_gui
    test_gui(__file__, PlayerList)