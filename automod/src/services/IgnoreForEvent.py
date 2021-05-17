class IgnoreForEvent:
    def __init__(self, bot):
        self.bot = bot
        self.messages = list()
        self.bans = list()
        self.unbans = list()

        self.valid_types = {
            "messages": self.messages,
            "bans_kicks": self.bans,
            "unbans": self.unbans
        }


    def add(self, _type, value):
        if not _type in self.valid_types:
            raise Exception("Invalid type")

        self.valid_types[_type].append(value)


    def get(self, _type, key):
        if not _type in self.valid_types:
            raise Exception("Invalid type")

        if not key in self.valid_types[_type]:
            return None
        
        return [_ for _ in self.valid_types[_type] if _ == key][0]

    
    def has(self, _type, key):
        if not _type in self.valid_types:
            raise Exception("Invalid type")

        if not key in self.valid_types[_type]:
            return False
        return True


    def remove(self, _type, key):
        if not _type in self.valid_types:
            raise Exception("Invalid type")
        
        if not key in self.valid_types[_type]:
            return None
        
        self.valid_types[_type].remove(key)
        return None