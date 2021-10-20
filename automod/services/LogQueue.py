import asyncio
import logging
import threading
import traceback


log = logging.getLogger(__name__)

class LogQueue:
    def __init__(self, bot):
        self.bot = bot
        self.loop = None
        self.__q = None


    async def do(self):
        obj = await self.__q.get()
        try:
            f = obj["func"]
            args = obj["args"]
            kwargs = obj["kwargs"]
            await f(*args, **kwargs)
        except Exception as ex:
            ex = traceback.format_exc()
            print("Error in function {} - {}".format(obj["func"], ex))
    

    async def listen(self):
        while True:
            await self.do()


    def add(self, func, *args, **kwargs):
        i = {
            "func": func,
            "args": args,
            "kwargs": kwargs
        }
        self.loop.call_soon_threadsafe(self.__q.put_nowait, i)


    def start(self):
        def f(): 
            l = asyncio.new_event_loop()

            self.loop = l
            self.__q = asyncio.Queue(loop=l)

            self.loop.run_until_complete(self.listen())

        t = threading.Thread(target=f)
        t.start()