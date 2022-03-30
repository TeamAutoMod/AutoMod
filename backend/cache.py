


class CacheMapping(dict):
    def __init__(self, size=1000):
        super().__init__()
        self.size = size


    def __setitem__(self, k, v):
        if not hasattr(self, "size"):
            self.size = 1000
        if len(self.__dict__) >= self.size:
            self.__dict__.pop(next(iter(self.__dict__)))
        self.__dict__[k] = v


    def update(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)
        if not hasattr(self, "size"):
            self.size = 1000
        if len(self.__dict__) >= self.size:
            self.__dict__.pop(next(iter(self.__dict__)))

    
class InternalCacheType(object):
    def __init__(self, _type, bot):
        self.bot = bot
        self._type = _type
        self.data = CacheMapping()
        for i in (getattr(self.bot.db, self._type)).find({}):
            if not str(i["id"]) in self.data:
                self.data[str(i["id"])] = i


    def get(self, _id, key):
        try:
            r = self.data[str(_id)].get(key, None)
        except KeyError:
            r = (getattr(self.bot.db, self._type)).get_from_db(_id, key)
            if r is not None:
                self.data[_id].update({
                    key: r
                }) 
        finally:
            return r


    def exists(self, _id):
        return str(_id) in self.data


    def update(self, _id, key, value):
        if str(_id) in self.data:
            self.data[str(_id)].update({
                key: value
            })


    def insert(self, _id, schema):
        if not str(_id) in self.data:
            self.data[str(_id)] = schema


    def get_all(self, _id):
        if str(_id) in self.data:
            return self.data[str(_id)]
        return None


    def delete(self, _id):
        if str(_id) in self.data:
            del self.data[str(_id)]


class InternalCache(object):
    def __init__(self, bot):
        self.bot = bot
        for i in bot.config.cache_options:
            setattr(self, i, InternalCacheType(i, bot))


    def new(self):
        for i in self.bot.config.cache_options:
            setattr(self, i, InternalCacheType(i, self.bot))