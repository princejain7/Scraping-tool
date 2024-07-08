import json


class Database:
    def __init__(self, filename):
        self.filename = filename

    def save_to_json(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)
