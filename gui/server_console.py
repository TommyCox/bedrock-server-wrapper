import tkinter
from tkinter.scrolledtext import ScrolledText
from basegui import GUI

class ServerConsole(GUI):
    def build_gui(self):
        self.build_console_window()
        self.build_command_input()
        self.build_command_spammer()

    def layout_config(self):
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.config(padx = 5)

    def build_console_window(self):
        title = tkinter.Label(self, text = "Server Console")
        title.grid(row = 0, column = 0, sticky = tkinter.W)

        scrollbox = ScrolledText(
            self,
            # width = self.total_width,
            # height = self.total_height,
            state = tkinter.DISABLED
        )
        scrollbox.grid(
            row = 1,
            column = 0,
            # rowspan = 1,
            columnspan = 2,
            padx = 5,
            sticky = tkinter.N+tkinter.S+tkinter.E+tkinter.W
        )

        # self.console = scrollbox


    def build_command_input(self):
        input1 = tkinter.Entry(self)
        input1.grid(row = 2, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = tkinter.W+tkinter.E)
        # input1.bind('<Return>', lambda event: self.__send_input(input1, True))

        # label1 = tkinter.Label(self, text = "Interact")
        # label1.grid(row = 5, column = 0, padx = 5, sticky = tkinter.E)

    def build_command_spammer(self):
        input2 = tkinter.Entry(self)
        input2.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = tkinter.W+tkinter.E)

        button = tkinter.Button(self, text = "SEND", height = 1, width = 4, padx = 10)
        button.grid(row = 3, column = 1)
        # button.configure(command = lambda: self.__send_input(input2,False))

        # label2 = tkinter.Label(self, text = "Send Command")
        # label2.grid(row = 6, column = 0, padx = 5, sticky = tkinter.E)

if __name__ == "__main__":
    # Test this module when run directly.
    from basegui import test_gui
    test_gui(__file__, ServerConsole)