import asyncio
import datetime
import os
import logging; log = logging.getLogger(__name__)



class Observer(object):
    def __init__(self, bot):
        self.bot = bot
        self.stamp_cache = {}
        for p in self.bot.config.plugins:
            path = f"backend/plugins/{p}.py"
            self.add_stamp_cache(p, path)


    def add_stamp_cache(self, name, path):
        with open(
            path, 
            "r", 
            encoding="utf8", 
            errors="ignore"
        ) as file: content = file.read()
        self.stamp_cache.update({
            name: {
                "file": path,
                "stamp": os.stat(path).st_mtime,
                "content": content
            }
        })

    
    async def watch(self):
        while True:
            await asyncio.sleep(0.3)
            for f, data in self.stamp_cache.items():
                st = os.stat(data["file"]).st_mtime
                if st != data["stamp"]:
                    self.stamp_cache[f]["stamp"] = st
                    with open(
                        data["file"], 
                        "r", 
                        encoding="utf8", 
                        errors="ignore"
                    ) as file: content = file.read()

                    if content != data["content"]:
                        try:
                            if f == "mod": 
                                _f = "moderation"
                            else:
                                _f = f
                            await self.bot.reload_plugin(_f)
                        except Exception as ex:
                            log.warn(f"Failed to hot reload {f} - {ex}")
                        else:
                            log.info(f"Hot reload completed for {f}")
                        finally:
                            self.bot.last_reload = datetime.datetime.utcnow().timestamp()
                            self.stamp_cache[f]["content"] = content


    async def start(self):
        log.info("Observer is starting")
        self.bot.loop.create_task(self.watch())