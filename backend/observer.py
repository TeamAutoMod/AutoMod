import asyncio
import datetime
import os
import inspect
from toolbox import to_json
import logging; log = logging.getLogger(__name__)



class Observer(object):
    def __init__(self, bot):
        self.bot = bot
        self.stamp_cache = {}
        for p in self.bot.config.plugins:
            path = f"backend/plugins/{p}.py"
            self.add_stamp_cache(p, path)
        
        for ext, f in {
            "config": "backend/config.json",
            "locale": "i18n/en_US.json"
        }.items():
            self.add_stamp_cache(ext, f)


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


    async def hot_reload(self, file, content, func, *func_args):
        try:
            if inspect.iscoroutinefunction(func):
                await func(*func_args)
            else:
                func(*func_args)
        except Exception as ex:
            log.warn(f"⚠️ Failed to hot reload {file} - {ex}")
        else:
            log.info(f"🔄 Hot reload completed for {file}")
        finally:
            self.bot.last_reload = datetime.datetime.utcnow().timestamp()
            self.stamp_cache[file]["content"] = content

    
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
                        if "/".join(data["file"].split("/")[:2]) == "backend/plugins":
                            await self.hot_reload(
                                f,
                                content,
                                self.bot.reload_plugin,
                                f
                            )
                        else:
                            await self.hot_reload(
                                f,
                                content,
                                getattr(self.bot, f).__init__,
                                self.bot if f != "config" else to_json(content)
                            )


    async def start(self):
        log.info("👀 Observer is starting")
        self.bot.loop.create_task(self.watch())