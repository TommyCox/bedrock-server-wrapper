import re

class Listener:
    def __init__(self, pattern, remove_timestamp = True):
        self.pattern = re.compile(pattern)
        if remove_timestamp:
            self.timestamp_pattern = re.compile(R"^(\[\d+\-\d\d\-\d\d \d\d:\d\d:\d\d \w+\])? (?P<message>.+)")
    
    def __call__(self, gui, message):
        # Remove timestamp if necessary.
        if self.timestamp_pattern:
            timestamp_match = self.timestamp_pattern.match(message)
            if timestamp_match:
                message = timestamp_match.group("message")

        matches = self.pattern.match(message)
        if matches:
            self.handler(gui, matches)

    def handler(self, gui, matches):
        pass