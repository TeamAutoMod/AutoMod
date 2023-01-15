# type: ignore

import asyncio
import datetime
import os
import inspect
from typing import Callable
from toolbox import to_json
import logging; log = logging.getLogger(__name__)



class Observer:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.stamp_cache = {}
        for p in self.bot.config.plugins:
            path = f"automod/plugins/{p}/plugin.py"
            self.add_stamp_cache(p, path)
        
        for ext, f in {
            "bot_config": "automod/config.json",
            "locale": "i18n/en_US.json"
        }.items():
            self.add_stamp_cache(ext, f)


    def add_stamp_cache(self, name: str, path: str) -> None:
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


    async def hot_reload(self, file: str, content: str, func: Callable, *func_args) -> None:
        try:
            if inspect.iscoroutinefunction(func):
                await func(*func_args)
            else:
                func(*func_args)
        except Exception as ex:
            log.warn(f"[Observer] Failed to hot reload {file} - {ex}", extra={"loc": f"PID {os.getpid()}"})
        else:
            log.info(f"[Observer] Hot reload completed for {file}", extra={"loc": f"PID {os.getpid()}"})
        finally:
            self.bot.last_reload = datetime.datetime.utcnow().timestamp()
            self.stamp_cache[file]["content"] = content

    
    async def watch(self) -> None:
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
                        self.stamp_cache[f]["data"] = content
                        if "/".join(data["file"].split("/")[:3]) == "automod/plugins":
                            await self.hot_reload(
                                f,
                                content,
                                self.bot.reload_plugin,
                                f
                            )
                        else:
                            if f == "bot_config": f = "config"
                            await self.hot_reload(
                                f,
                                content,
                                getattr(self.bot, f).__init__,
                                self.bot if f != "config" else to_json(content)
                            )


    async def start(self) -> None:
        log.info("[Observer] Observer is starting", extra={"loc": f"PID {os.getpid()}"})
        self.bot.loop.create_task(self.watch())