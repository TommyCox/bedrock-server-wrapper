import tkinter

from basegui import GUI
from sidebar import SideBar
from server_console import ServerConsole

class MainApp(GUI):
    def build_gui(self):
        self.__top_level_menu()
        sidebar = SideBar(self, width = 30)
        console = ServerConsole(self)
        sidebar.grid(row = 0, column = 0, sticky = self.onHeight)
        console.grid(row = 0, column = 1, sticky = self.onAll)

    def layout_config(self):
        # self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.rowconfigure(0, weight = 1)

    def __top_level_menu(self):
        menu = tkinter.Menu(self)
        self.master.config(menu=menu)

        file_menu = tkinter.Menu(menu)
        # file_menu.add_command(label="View Folder", command=self.wrapcom_view)
        file_menu.add_command(label="View Folder", command=self.placeholder) # TODO: Delete this debugging line.
        exit_submenu = tkinter.Menu(file_menu)
        # exit_submenu.add_command(label="Exit", command=self.wrapcom_exit)
        exit_submenu.add_command(label="Exit", command=self.placeholder) # TODO: Delete this debugging line.
        exit_submenu.add_command(label = "Force Exit", command = exit)
        file_menu.add_cascade(label = "Exit", menu = exit_submenu)
        menu.add_cascade(label="File", menu=file_menu)

        update_menu = tkinter.Menu(menu)
        # update_menu.add_command(label="Update Server", command=lambda: self.wrapcom_update("server"))
        update_menu.add_command(label="Update Server", command=lambda: self.placeholder("server")) # TODO: Delete this debugging line.
        # update_menu.add_command(label="Update Wrapper", command=lambda: self.wrapcom_update("wrapper"))
        update_menu.add_command(label="Update Wrapper", command=lambda: self.placeholder("wrapper")) # TODO: Delete this debugging line.
        menu.add_cascade(label="Update", menu=update_menu)

    def placeholder(self, *args, **kwargs):
        print("Placeholder triggered!")
        print(f"Args: {args}")
        print(f"Kwargs: {kwargs}")

if __name__ == "__main__":
    # Test this module when run directly.
    from basegui import test_gui
    test_gui(__file__, MainApp)