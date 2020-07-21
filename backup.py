from listeners import Listener
import os, re, errno
from datetime import datetime
from pathlib import Path

class WorldBackup(Listener):
    def __init__(self, backup_location, add_timestamp=True):
        self.backup_ready = False
        self.finished = False

        self.data_pattern = re.compile(R"\s?(.*?):(\d+),?")
        super().__init__(self.data_pattern.findall)

        self.backup_dir = Path(backup_location)
        self.add_timestamp = add_timestamp

    def handler(self, gui, file_list):
        self.backup_ready = True # This is the signal to stop calling save query.
        time = datetime.now()
        timestamp = "%Y_%m_%d_%H%M " if self.add_timestamp else ""
        for filename, filesize in file_list:
            filepath = Path(gui.server_dir, "worlds") / filename
            savepath = self.backup_dir / (time.strftime(timestamp) + filename)
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
        self.finished = True