import discord.http
discord.http.Route.BASE = "https://discordapp.com/api/v6" #v6 > v7

from Bot.AutoMod import AutoMod
from log_setup import setup_logging 
import sys
import os
import asyncio

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())





def boot_bot(shards):
    from Utils.Utils import clean_shutdown, init_config
    init_config()
    bot = AutoMod(shards=shards)
    bot.remove_command("help")

    try:
        bot.run()
    except KeyboardInterrupt:
        try:
            for t in asyncio.all_tasks():
                try:
                    t.cancel()
                except:
                    continue
        except RuntimeError:
            pass
        try:
            asyncio.run(bot.close())
            self.loop.stop()
            self.loop.close()
        except:
            pass
        quit()
    except Exception:
        pass
        



if __name__ == "__main__":
    from Utils.Utils import parse_args
    shards = parse_args().total_shards

    with setup_logging():
        boot_bot(shards)