from pathlib import Path
import re
import tkinter
from tkinter.scrolledtext import ScrolledText
from server_controller import BDS_Wrapper as ServerInstance
from player_list import PlayerList

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

		self.__make_menu()
		self.__make_left()
		self.__make_right()

		self.server_instance = None
		self.server_dir = self.default_server_dir if server_dir is None else server_dir
		self.exec_name = self.default_exec_name if exec_name is None else exec_name
		self.autoscroll_log = True # Might make this setting edit-able later.
		self.log_listeners = set()

	def __make_menu(self):
		menu = tkinter.Menu(self)
		self.config(menu=menu)

		file = tkinter.Menu(menu)
		file.add_command(label="Exit", command=exit)
		menu.add_cascade(label="File", menu=file)

	def __make_left(self):
		# Set up left-side GUI elements.

		title = tkinter.Label(self, text = "Special Controls")
		title.grid(row = 0, column = 0)

		# TEMP: Disable button until implemented.
		button1 = tkinter.Button(self, text = "Start Server", width = 15, height = 5)
		button1.grid(row = 1, column = 0)
		button1.config(command=self.start_server)

		# TEMP: Disable button until implemented.
		button2 = tkinter.Button(self, text = "Backup World", width = 15, height = 5, state = tkinter.DISABLED)
		button2.grid(row = 2, column = 0)

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

		input2 = tkinter.Entry(self)
		input2.grid(row = 6, column = 1, padx = 5, pady = 5, sticky = tkinter.W+tkinter.E)

		button = tkinter.Button(self, text = "SEND", padx = 15)
		button.grid(row = 6, column = 2)

		self.console = scrollbox
		self.input = input1
		self.alt_input = input2
		self.send_button = button

	def __interpret(self, message, from_user):
		if not from_user:
			# Extract useful external data.
			# Ex. Tracking player connections/disconnections.
			# self.console_thread.join() # Call this when the server outputs the shutdown message to the log?
			for listener in self.log_listeners:
				listener(self, message)
			pass
		# else:
		# 	# Check for meta-commands to this program if implemented.
		# 	pass

	def __send_input(self, input_source, input_handler, clear_input, echo = True):
		text = input_source.get()
		input_handler(text)
		if echo:
			self.write_console(text+"\n", from_user = True)
		if clear_input:
			input_source.delete(0, tkinter.END)
			
	def add_listener(self, listener):
		self.log_listeners.add(listener)

	def bind_inputs(self, input_handler):
		self.input.bind('<Return>', lambda event: self.__send_input(self.input,input_handler,True))
		self.send_button.configure(command = lambda: self.__send_input(self.alt_input,input_handler,False))

	def clear_textbox(self, textbox):
		textbox.configure(state = tkinter.NORMAL)
		textbox.delete("1.0", tkinter.END)
		textbox.configure(state = tkinter.DISABLED)

	def remove_listener(self, listener):
		self.log_listeners.remove(listener)

	def start_server(self):
		if self.server_instance is None or not self.server_instance.is_running():
			self.server_instance = ServerInstance(Path(self.server_dir) / self.exec_name)
			self.console_thread = self.server_instance.read_output(output_handler = self.write_console)
			self.console_thread.start()
			self.bind_inputs(self.server_instance.write)

			self.log_listeners = set() # Create a set holding listening functions.
			self.log_listeners.add(PlayerList()) # Create a new player list and add to listeners.

	def write_console(self, text, from_user = False):
		self.write_textbox(self.console, text)
		self.__interpret(text, from_user)

	def write_textbox(self, textbox, text):
		textbox.configure(state = tkinter.NORMAL)
		textbox.insert(tkinter.END, text)
		textbox.configure(state = tkinter.DISABLED)
		if self.autoscroll_log:
			textbox.yview(tkinter.END)

if __name__ == "__main__":
	ui = GUI()

	ui.bind_inputs(print)

	ui.mainloop()
