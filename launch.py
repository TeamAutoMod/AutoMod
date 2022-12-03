# type: ignore

import asyncio
import discord
from discord.ext import commands

import sys
import inspect
import signal as sig_lib
import logging; log = logging.getLogger(__name__)

from backend.bot import ShardedBotInstance



async def _shutdown(
    bot: ShardedBotInstance,
    sig: str
) -> None:
    log.info(f"Shutting down (triggered by {sig})")
    try: 
        await bot.close()
    except Exception: 
        pass
    else:
        try:
            bot.loop.close()
        except Exception:
            pass
        finally:
            sys.exit(0)
        

if __name__ == "__main__":
    if not inspect.iscoroutinefunction(commands.Bot.load_extension):
        print("Your discord.py version is too old. Install a newer one using the following command: \npip install git+https://github.com/Rapptz/discord.py"); sys.exit(1)
    else:
        __instance = ShardedBotInstance()

        try:
            for sn in ["SIGINT", "SIGTERM"]:
                asyncio.get_event_loop().add_signal_handler(
                    getattr(sig_lib, sn), 
                    lambda: asyncio.ensure_future(_shutdown(__instance, sn))
                )
        except Exception: pass

        try:
            __instance.run()
        except Exception as ex:
            log.error(f"Error in run() function - {ex}")
            loop = asyncio.get_event_loop()
            if loop != None:
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
            else:
                loop = asyncio.new_event_loop()
            asyncio.run_coroutine_threadsafe(
                _shutdown(__instance, "__main__"),
                loop=loop
            )