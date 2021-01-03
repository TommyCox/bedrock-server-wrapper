from listeners import Listener

class PlayerList(Listener):
    def __init__(self):
        connection_pattern = R"Player (?P<type>dis)?connected: (?P<username>.+), xuid: (?P<xuid>\d+)"
        super().__init__(connection_pattern)
        self.players = set()
    
    def handler(self, gui, matches):
        self.update_list(matches)
        self.update_gui(gui)

    def update_gui(self, gui):
        gui.clear_textbox(gui.player_list)
        gui.write_textbox(gui.player_list, "\n".join(self.players))

    def update_list(self, matches):
        player_name = matches.group('username')
        quitting = (matches.group('type') == "dis")
        if player_name:
            if quitting:
                try:
                    self.players.remove(player_name)
                except KeyError as error:
                    print(f"Attempted to remove someone ({error}) who never joined!")
            else:
                self.players.add(player_name)

if __name__ == "__main__":
    print(f"Testing {__file__}")

    class FakeGui():
        def __init__(self):
            self.player_list = "the player textbox"

        def clear_textbox(self, textbox):
            print(f"Cleared {textbox}.")

        def write_textbox(self, textbox, text):
            print(f"Wrote '{text}' in {textbox}.")

    def connect_string(name, id):
        return f"Player connected: {name}, xuid: {id}"

    def disconnect_string(name, id):
        return f"Player disconnected: {name}, xuid: {id}"

    gui = FakeGui()
    pl_listener = PlayerList()

    # Test with random string.
    pl_listener(gui, "Play0r eez deehzconnaykt.")

    # Test with correct connection string.
    test_string = connect_string("foo", 1337)
    pl_listener(gui, test_string)
    # Test with incorrect disconnection string.
    test_string = disconnect_string("bar", 9001)
    pl_listener(gui, test_string)
    # Test with correct disconnection string.
    test_string = disconnect_string("foo", 1337)
    pl_listener(gui, test_string)

    # Test with players named "connected", "xuid" and "dis"
    test_string = connect_string("connected", 8)
    pl_listener(gui, test_string)
    test_string = connect_string("xuid", 9)
    pl_listener(gui, test_string)
    test_string = connect_string("dis", 10)
    pl_listener(gui, test_string)
    
    test_string = disconnect_string("xuid", 9)
    pl_listener(gui, test_string)
    test_string = disconnect_string("connected", 8)
    pl_listener(gui, test_string)
    test_string = disconnect_string("dis", 10)
    pl_listener(gui, test_string)

    print("Test completed.")