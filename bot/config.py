import json


class Config(dict):

    def __init__(self, data=None):
        if data is None:
            data = {}
        super().__init__(data)

    def load(self):
        with open('config.json', 'r') as f:
            data = json.load(f)
        return data

    def get(self, key, default=None):
        data = self.load()
        return data.get(key, default)

    def __getitem__(self, key):
        data = self.load()
        return data[key]

    def __getattr__(self, key):
        data = self.load()
        return data[key]


config = Config()
