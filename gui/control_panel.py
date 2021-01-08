import tkinter
from basegui import GUI

class ControlPanel(GUI):
    def build_gui(self):
        title = tkinter.Label(self, text = "Control Panel")
        title.grid(row = 0, column = 0, sticky = self.onAll)

        button1 = tkinter.Button(self, text = "Start Server")
        button1.grid(row = 1, column = 0, sticky = self.onAll)
        # button1.config(command=self.start_server)

        button2 = tkinter.Button(self, text = "Backup World")
        button2.grid(row = 2, column = 0, sticky = self.onAll)
        # button2.config(command=self.backup_world)

        # self.start_button = button1
        # self.backup_button = button2
    
    def layout_config(self):
        self.columnconfigure(0, weight = 1)
        self.rowconfigure((1,2), weight = 1)
        self.config(padx = 10, pady = 10)


if __name__ == "__main__":
    # Test this module when run directly.
    from basegui import test_gui
    test_gui(__file__, ControlPanel)