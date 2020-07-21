from pathlib import Path
import os, sys, shutil
import re, subprocess
from contextlib import contextmanager

import tkinter
from tkinter.scrolledtext import ScrolledText

from server_controller import BDS_Wrapper as ServerInstance
from player_list import PlayerList
from updater import ServerUpdater, WrapperUpdater
from backup import BackupListener, make_timestamp

class GUI(tkinter.Tk):
	default_server_dir = "minecraft_server"
	default_exec_name = "bedrock_server.exe"

	def __init__(self, *args, server_dir = None, exec_name = None, **kwargs):
		super().__init__(*args, **kwargs)

		self.title('Bedrock Server Wrapper')
		self.geometry('700x700')
		self.minsize(700,700)

		self.grid()
		self.grid_columnconfigure(0, pad = 5)
		self.grid_columnconfigure(1, weight = 1)
		self.grid_columnconfigure(2, pad = 5)
		self.grid_rowconfigure(2, pad = 5)
		self.grid_rowconfigure(4, weight = 1)

		self.option_add("*tearOff", tkinter.FALSE)
		self.__make_menu()
		self.__make_left()
		self.__make_right()

		self.server_instance = None
		self.server_dir = self.default_server_dir if server_dir is None else server_dir
		self.exec_name = self.default_exec_name if exec_name is None else exec_name
		self.autoscroll_log = True # Might make this setting edit-able later.
		
		self.log_listeners = set()
		self.make_command_lookup()
		self.protocol("WM_DELETE_WINDOW", self.wrapcom_exit)

	def __make_menu(self):
		menu = tkinter.Menu(self)
		self.config(menu=menu)

		file_menu = tkinter.Menu(menu)
		file_menu.add_command(label="Exit", command=exit)
		menu.add_cascade(label="File", menu=file_menu)

		update_menu = tkinter.Menu(menu)
		update_menu.add_command(label="Update Server", command=lambda event: self.wrapcom_update("server"))
		update_menu.add_command(label="Update Wrapper", command=lambda event: self.wrapcom_update("wrapper"))
		menu.add_cascade(label="Update", menu=update_menu)

	def __make_left(self):
		# Set up left-side GUI elements.

		title = tkinter.Label(self, text = "Special Controls")
		title.grid(row = 0, column = 0)

		# TEMP: Disable button until implemented.
		button1 = tkinter.Button(self, text = "Start Server", width = 15, height = 5)
		button1.grid(row = 1, column = 0)
		button1.config(command=self.start_server)

		# TEMP: Disable button until implemented.
		button2 = tkinter.Button(self, text = "Backup World", width = 15, height = 5)
		button2.grid(row = 2, column = 0)
		button2.config(command=self.backup_world)

		title2 = tkinter.Label(self, text = "Players")
		title2.grid(row = 3, column = 0, sticky = tkinter.N)

		scrollbox = ScrolledText(self, width = 20, height = 10, state = tkinter.DISABLED)
		scrollbox.grid(row = 4, column = 0, sticky = tkinter.N+tkinter.S)

		label1 = tkinter.Label(self, text = "Interact")
		label1.grid(row = 5, column = 0, padx = 5, sticky = tkinter.E)

		label2 = tkinter.Label(self, text = "Send Command")
		label2.grid(row = 6, column = 0, padx = 5, sticky = tkinter.E)

		self.start_button = button1
		self.backup_button = button2
		self.player_list = scrollbox

	def __make_right(self):
		# Set up right-side GUI elements.

		title = tkinter.Label(self, text = "Server Console")
		title.grid(row = 0, column = 1, sticky = tkinter.W)

		scrollbox = ScrolledText(self, width = 50, height = 30, state = tkinter.DISABLED)
		scrollbox.grid(row = 1, column = 1, rowspan = 4, columnspan = 2, padx = 5, sticky = tkinter.N+tkinter.S+tkinter.E+tkinter.W)

		input1 = tkinter.Entry(self)
		input1.grid(row = 5, column = 1, columnspan = 2, padx = 5, pady = 5, sticky = tkinter.W+tkinter.E)
		input1.bind('<Return>', lambda event: self.__send_input(input1, True))

		input2 = tkinter.Entry(self)
		input2.grid(row = 6, column = 1, padx = 5, pady = 5, sticky = tkinter.W+tkinter.E)

		button = tkinter.Button(self, text = "SEND", padx = 15)
		button.grid(row = 6, column = 2)
		button.configure(command = lambda: self.__send_input(input2,False))

		self.console = scrollbox

	def __output_handler(self, text):
		self.write_console(text)
		self.__interpret(text)

	def __interpret(self, message):
		"""Reads input from the server or user and calls listeners."""
		# Send server messages to listeners.
		for listener in self.log_listeners.copy():
			listener(self, message)
		pass

	def __send_input(self, input_source, clear_input, echo = True):
		"""Sends input from textbox to input handler function.
		
		This function sends text in a textbox (input_source) to a handler
		function (input_handler) and manages the textbox (clears input if clear_input is set).

		Inputs are echoed to the console unless echo is set to false.
		"""
		text = input_source.get()
		if echo:
			self.write_console(f"[USER] {text}\n")
		if clear_input:
			input_source.delete(0, tkinter.END)

		match = self.meta_pattern.match(text)
		if match:
			# Interpret as command to wrapper.
			# Default to help if unknown command.
			arguments = match.group("arguments").split() if match.group("arguments") else []
			func = self.wrapper_commands.get(match.group("command"), self.wrapcom_help)
			try:
				func(*arguments)
			except TypeError as error:
				match = re.match(R".+\(\) takes (\d+) positional arguments? but (\d+) were given", str(error))
				if match:
					self.message_user("Incorrect number of arguments were passed.")
					self.message_user(f"Expected {int(match.group(1)) - 1} but got {int(match.group(2)) - 1}.")
				else:
					raise error
		else:
			# Interpret as command to server.
			self.server_input(text)
			
	def add_listener(self, listener):
		"""Adds a listener to call whenever a server message apperars in the log."""
		self.log_listeners.add(listener)

	def bind_inputs(self, input_handler):
		"""Specifies what function should handle user inputs from the command lines."""
		self.server_input = input_handler

	def backup_world(self, backup_location = "backups", add_timestamp = True):
		POLLING_INTERVAL = 100 # Time in ms.
		save_path = Path(backup_location)
		if not os.path.exists(save_path):
			os.makedirs(save_path)
		if self.server_instance and self.server_instance.is_running():
			listener = BackupListener(save_path, add_timestamp)
			self.add_listener(listener)
			self.send_input("save hold")
			# Backup method:
			# Call "save hold".
			# Repeatedly call "save query" until file list is returned.
			# Save and truncate files.
			# Call "save resume".
			def finish_loop():
				if listener.finished:
					self.send_input("save resume")
					self.remove_listener(listener)
				else:
					self.after(POLLING_INTERVAL, finish_loop)
			
			def query_loop():
				self.send_input("save query")
				if listener.backup_ready:
					self.after(POLLING_INTERVAL, finish_loop)
				else:
					self.after(POLLING_INTERVAL, query_loop)
			
			self.after(POLLING_INTERVAL, query_loop)
		else:
			worldpath = Path(self.server_dir) / "worlds"
			with os.scandir(worldpath) as iterator:
				for entry in iterator:
					if entry.is_dir():
						worldname = entry.name
						shutil.copytree(worldpath / worldname, Path(backup_location) / f"{make_timestamp()} {worldname}")

	def clear_textbox(self, textbox):
		"""Clears a textbox."""
		textbox.configure(state = tkinter.NORMAL)
		textbox.delete("1.0", tkinter.END)
		textbox.configure(state = tkinter.DISABLED)

	def remove_listener(self, listener):
		"""Removes a listener that was listening to the log of server messages."""
		self.log_listeners.remove(listener)

	def message_user(self, message):
		"""Displays a message from the wrapper to the user."""
		text = message.strip()
		if not (text == ""):
			self.write_console(f"[WRAPPER] {text}\n")

	def send_input(self, text):
		"""Sends an input string to the server."""
		self.server_input(text)
		self.write_console(f"[AUTOMATED] {text}\n")

	def start_server(self):
		"""Starts the minecraft server."""
		if self.server_instance is None or not self.server_instance.is_running():
			self.server_instance = ServerInstance(Path(self.server_dir) / self.exec_name)
			self.console_thread = self.server_instance.read_output(output_handler = self.__output_handler)
			self.console_thread.start()
			self.bind_inputs(self.server_instance.write)

			self.log_listeners.clear() # Create a set holding listening functions.
			self.add_listener(PlayerList()) # Create a new player list and add to listeners.

	def stop_server(self, post_stop = None, *args):
		# This is a really ugly function.
		MAX_WAIT_DEPTH = 15 # Maximum number of WAIT_INTERVAL to wait.
		WAIT_INTERVAL = 1000 # In ms.
		if self.server_instance and self.server_instance.is_running():
			self.message_user("Stopping server.")
			self.send_input("stop")

			def pause(action, depth, *args):
				if depth > MAX_WAIT_DEPTH:
					self.message_user("Server did not stop in time. Cancelling action.")
					return
				if self.server_instance and self.server_instance.is_running():
					# Go another level.
					self.message_user("Waiting for server to stop.")
					self.after(WAIT_INTERVAL, pause, action, depth + 1, *args)
				else:
					self.message_user("Server stop confirmed.")
					action(*args)
			if post_stop:
				self.after(WAIT_INTERVAL, pause, post_stop, 0, *args)
		else:
			if post_stop:
				post_stop(*args)

	def write_console(self, text):
		"""Writes a message to console."""
		self.write_textbox(self.console, text)
		if self.autoscroll_log:
			self.console.yview(tkinter.END)

	def write_textbox(self, textbox, text):
		"""Writes text to a specified textbox.

		This funtion enables a textbox, writes the selected text to the end,
		then disables the textbox again.
		"""
		textbox.configure(state = tkinter.NORMAL)
		textbox.insert(tkinter.END, text)
		textbox.configure(state = tkinter.DISABLED)

	# --------------------------- #
	# User Commands
	# --------------------------- #

	def make_command_lookup(self):
		self.meta_pattern = re.compile(R"^/(?P<command>\S+)\s?(?P<arguments>.+)?")
		self.wrapper_commands = {
			"help": self.wrapcom_help,
			"exit": self.wrapcom_exit,
			"restart": self.wrapcom_restart,
			"update": self.wrapcom_update,
			"viewdir": self.wrapcom_view,
		}

	def wrapcom_exit(self):
		"""Stops the server and closes the wrapper program."""
		self.stop_server(post_stop=exit)

	def wrapcom_help(self, *args, **kwargs):
		"""Displays this help message."""
		help_message = "This is a help message."
		help_message += "\n" + "Use the form /command to send commands to the wrapper."
		help_message += "\n" + "Existing Commands:"
		# Generate command list using docstrings.
		for command, func in self.wrapper_commands.items():
			documentation = func.__doc__ if func.__doc__ else ""
			delimiter = " - " if not documentation == "" else ""
			help_message += "\n  " + f"{command}{delimiter}{documentation}"
		self.message_user(help_message)

	def wrapcom_restart(self):
		"""Stops the server and restarts the wrapper program."""
		def restart_program():
			# Flush any open files here before restarting.
			os.execv(sys.executable, [sys.executable, __file__] + sys.argv)
		self.stop_server(post_stop=restart_program)

	def wrapcom_update(self, component = "", *args):
		"""Access updater. Use update help for details."""
		if component == "server":
			overwrite = (args[0] == "overwrite") if len(args) >= 1 else False
			locale = (args[1]) if len(args) >= 2 else "en-us"
			updater = ServerUpdater(self.server_dir, overwrite, locale)
		elif component == "wrapper":
			updater = WrapperUpdater()
			restart_wrapper = True
		else:
			update_help_message = "Gives access to update functions."
			update_help_message += "\n  " + "update server [keep|overwrite] [locale] - Update the server program."
			update_help_message += "\n    " + "[keep|overwrite] - Defaults to keep. If set to overwrite, server settings will not be preserved."
			update_help_message += "\n    " + "[locale] - Locale used to access minecraft website. Defaults to en-us. https://minecraft.net/{locale}/download"
			update_help_message += "\n  " + "update wrapper [branch] - Update the wrapper program."
			update_help_message += "\n    " + "[branch] - GitHub branch to use. Defaults to master."
			self.message_user(update_help_message)
			return
		if self.server_instance and self.server_instance.is_running():
			self.message_user("Server is running. Please stop server before updating.")
		else:
			self.message_user(f"Updating {component}.")
			completed = updater.update()
			if completed:
				self.message_user("Update complete.")
				if restart_wrapper:
					self.wrapcom_restart()
			else:
				self.message_user("Update was not completed.")

	def wrapcom_view(self):
		"""Opens the folder containing the server."""
		if sys.platform == "win32":
			os.startfile(self.server_dir)
		elif sys.platform == "darwin":
			subprocess.Popen(["open", self.server_dir])
		elif sys.platform == "linux":
			subprocess.Popen(["xdg-open", self.server_dir])
		else:
			raise Exception("Unsupported platform.")

@contextmanager
def output_redirector(output_handler):
	"""A cool hack to redirect print statements to output_handler.

	WARNING: If output_handler calls print there will be infinite recursion.
				This includes indirectly calling print through another function.
	"""
	class FakeFile():
		def write(self, string):
			output_handler(string)

	file_like = FakeFile()
	old = sys.stdout
	sys.stdout = file_like
	try:
		yield file_like
	finally:
		sys.stdout = old

if __name__ == "__main__":
	ui = GUI()

	ui.bind_inputs(print)

	ui.mainloop()
