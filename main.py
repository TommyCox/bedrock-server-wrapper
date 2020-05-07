# ---------------------------------------------------------------------------- #
# Libraries
# ---------------------------------------------------------------------------- #
from pathlib import Path

# ---------------------------------------------------------------------------- #
# Local Modules
# ---------------------------------------------------------------------------- #
from server_controller import BDS_Wrapper as StartServer
from wrapper_gui import GUI as MakeGUI

# ---------------------------------------------------------------------------- #
# Actual Program
# ---------------------------------------------------------------------------- #
server_path = Path("minecraft_server/bedrock_server.exe")

gui = MakeGUI()

server = StartServer(server_path)
console = server.read_output(output_handler = gui.write_console)
console.start()

gui.bind_inputs(server.write)

gui.mainloop()

if server.is_running():
	server.write("stop")

console.join()
