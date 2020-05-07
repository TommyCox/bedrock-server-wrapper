import subprocess
import shlex
import threading

class BDS_Wrapper(subprocess.Popen):
	def __init__(self, exec_path, **kwargs):
		super().__init__(
			exec_path,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			**kwargs
		)

	def read_output(self, output_handler):
		# Spawns a new thread to read the output.
		# The thread calls output_handler with the string that was read.
		# Returns the thread.
		def worker():
			for line in iter(self.stdout.readline, b''):
				output_handler(line.decode("utf-8"))

		return threading.Thread(target=worker)

	def is_running(self):
		return self.poll() == None

	def write(self, command_string, terminator = "\n"):
		if self.is_running():
			data = command_string + terminator
			self.stdin.write(data.encode())
			self.stdin.flush()
			return True
		else:
			return False