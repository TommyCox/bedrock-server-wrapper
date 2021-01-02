from listeners import Listener
import os, re, errno
from datetime import datetime
from pathlib import Path
from threading import Lock

class BackupListener(Listener):
    def __init__(self, backup_location, add_timestamp=True):
        self.internal_lock = Lock()
        self.finished = False

        self.data_pattern = re.compile(R"\s?(.*?):(\d+),?")
        super().__init__(self.data_pattern.findall)

        self.backup_dir = Path(backup_location)
        self.add_timestamp = add_timestamp

    def handler(self, gui, file_list):
        if self.internal_lock.acquire(False):
            timestamp = f"{make_timestamp()} " if self.add_timestamp else ""
            for filename, filesize in file_list:
                filepath = Path(gui.server_dir, "worlds") / filename
                savepath = self.backup_dir / (timestamp + filename)
                if not os.path.exists(os.path.dirname(savepath)):
                    try:
                        os.makedirs(os.path.dirname(savepath))
                    except OSError as error:
                        if error.errno != errno.EEXIST:
                            raise error
                with open(filepath, "rb") as oldfile:
                    with open(savepath, "wb+") as newfile:
                        newfile.write(oldfile.read(int(filesize)))
            gui.message_user("Finished backing up files.")
            self.internal_lock.release()
            self.finished = True

def make_timestamp():
    return datetime.now().strftime("%Y_%m_%d_%H%M")