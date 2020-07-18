from pathlib import Path
import os, shutil
import urllib.request
import hashlib
import zipfile, tempfile

class WebConnection():
    def __init__(self, url):
        self.url = url
        self.__access()

    def __access(self):
        self.response = urllib.request.urlopen(self.url)
        self.read = self.response.read

    def download_to(self, file):
        file.write(self.response.read())

# Working update code for reference.
# def update_wrapper(branch="master"):
#     repo = "bedrock-server-wrapper"
#     url = f"https://github.com/TommyCox/{repo}/archive/{branch}.zip"
#     types_to_update = (".py")
#     destination_dir = Path.cwd()
#     try:
#         print(f"Connecting to {url}")
#         files = WebConnection(url)
#         with tempfile.TemporaryFile() as newfile:
#             print("Downloading files.")
#             files.download_to(newfile)
#             #TODO: Do version checking, checksums, or whatever here.
#             print("Unzipping archive...")
#             with zipfile.ZipFile(newfile) as zipped:
#                 for zipinfo in zipped.infolist():
#                     if zipinfo.filename.endswith(types_to_update):
#                         print(f"Found file '{zipinfo.filename}'")
#                         prefix = f"{repo}-{branch}/"
#                         zipinfo.filename = zipinfo.filename.replace(prefix, "" , 1)
#                         print(f"Extracting as {zipinfo.filename}")
#                         zipped.extract(zipinfo, destination_dir)
#     except urllib.error.HTTPError as http_error:
#         print(f"HTTP Error: {http_error}")
#         return False
#     return True

class Updater():
    def connect(self):
        try:
            return WebConnection(self.url)
        except urllib.error.HTTPError as http_error:
            print(f"HTTP Error: {http_error}")
            return None

    def unzip(self, downloaded_file):
        with zipfile.ZipFile(downloaded_file) as zipped:
            for zipinfo in zipped.infolist():
                if self.extract_this(zipinfo):
                    zipped.extract(zipinfo, self.destination_dir)

class ServerUpdater(Updater):
    def __init__(self, server_dir = "minecraft_server", locale = "en-us"):
        self.destination_dir = Path(server_dir)
        self.url = f"https://minecraft.net/{locale}/download/server/bedrock"
        self.types_to_update = (".py")


class WrapperUpdater(Updater):
    def __init__(self, branch = "master", repo = "bedrock-server-wrapper"):
        self.destination_dir = Path.cwd()
        self.repo = repo
        self.branch = branch
        self.url = f"https://github.com/TommyCox/{repo}/archive/{branch}.zip"
        self.types_to_update = (".py")

    def extract_this(self, zipinfo):
        # Make modifications to extraction.
        prefix = f"{self.repo}-{self.branch}/"
        zipinfo.filename = zipinfo.filename.replace(prefix, "" , 1)
        # Return boolean for extraction conditions.
        return zipinfo.filename.endswith(self.types_to_update)

    def update(self):
        # Connect to url.
        connection = self.connect()

        # Download files.
        with tempfile.TemporaryFile() as newfile:
            connection.download_to(newfile)
        
        #TODO: Do version checking, checksums, or whatever here.

        # Extract files to destination directory..
            self.unzip(newfile)

        return True

if __name__ == "__main__":
    print("Test start!")
    updater = WrapperUpdater()
    updater.update()
    print("Test end!")