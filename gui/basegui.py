import tkinter

class GUI(tkinter.Frame):
    onWidth = tkinter.E + tkinter.W
    onHeight = tkinter.N + tkinter.S
    onAll = onHeight + onWidth

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build_gui()
        self.layout_config()
    
    def build_gui(self):
        """Virtual method to build gui."""
        pass

    def layout_config(self):
        """Virtual method for optional layout configuration."""
        pass

def test_gui(source_file, ClassToTest, size = (700, 700), minsize = (500,500)):
    from os.path import basename
    root = tkinter.Tk()
    root.title(f"[GUI_TEST] {basename(source_file)}")
    root.geometry("{}x{}".format(*size))
    root.minsize(*minsize)
    root.option_add("*tearOff", tkinter.FALSE)

    instance = ClassToTest(root)
    instance.grid(sticky = tkinter.N + tkinter.S + tkinter.E + tkinter.W)
    root.columnconfigure(0, weight = 1)
    root.rowconfigure(0, weight = 1)
    root.mainloop()