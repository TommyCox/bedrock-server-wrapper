import re

class PlayerList():
    def __init__(self):
        self.players = set()
        self.pattern = re.compile(R"Player (?P<type>dis)?connected: (?P<username>.+), xuid: (?P<xuid>\d+)")
    
    def __call__(self, gui, message):
        matches = self.pattern.match(message)
        if matches:
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

