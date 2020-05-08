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

def update_wrapper(branch="master"):
    repo = "bedrock-server-wrapper"
    url = f"https://github.com/TommyCox/{repo}/archive/{branch}.zip"
    types_to_update = (".py")
    destination_dir = Path.cwd()
    try:
        print(f"Connecting to {url}")
        files = WebConnection(url)
        with tempfile.TemporaryFile() as newfile:
            print("Downloading files.")
            files.download_to(newfile)
            #TODO: Do version checking, checksums, or whatever here.
            print("Unzipping archive...")
            with zipfile.ZipFile(newfile) as zipped:
                for zipinfo in zipped.infolist():
                    if zipinfo.filename.endswith(types_to_update):
                        print(f"Found file '{zipinfo.filename}'")
                        prefix = f"{repo}-{branch}/"
                        zipinfo.filename = zipinfo.filename.replace(prefix, "" , 1)
                        print(f"Extracting as {zipinfo.filename}")
                        zipped.extract(zipinfo, destination_dir)
    except urllib.error.HTTPError as http_error:
        print(f"HTTP Error: {http_error}")
        return False
    return True

if __name__ == "__main__":
    print("Test start!")
    update_wrapper()
    print("Test end!")