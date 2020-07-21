import re

class Listener:
    def __init__(self, pattern_tester, remove_timestamp = True):
        if isinstance(pattern_tester, str):
            pattern = re.compile(pattern_tester)
            self.test_pattern = pattern.match
        else:
            self.test_pattern = pattern_tester
        if remove_timestamp:
            self.timestamp_pattern = re.compile(R"^(\[\d+\-\d\d\-\d\d \d\d:\d\d:\d\d \w+\])? (?P<message>.+)")
    
    def __call__(self, gui, message):
        # Remove timestamp if necessary.
        if self.timestamp_pattern:
            timestamp_match = self.timestamp_pattern.match(message)
            if timestamp_match:
                message = timestamp_match.group("message")

        result = self.test_pattern(message)
        if result:
            self.handler(gui, result)

    def handler(self, gui, matches):
        pass