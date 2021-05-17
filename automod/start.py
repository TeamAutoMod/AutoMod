import discord.http
discord.http.Route.BASE = "https://discordapp.com/api/v6"

import os
import json
import asyncio


from src import Harpoon
from src.logger import SetupLogging



def run(bot):
    bot.remove_command("help")
    bot.run()


if __name__ == "__main__":
    if not os.path.exists("./config.json"):
        print("Missing config file")
        exit(1)

    config = json.load(open("./config.json", "r", closefd=True))
    automod = Harpoon(config)

    with SetupLogging():
        try:
            run(automod)
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
                asyncio.run(automod.close())
                automod.loop.stop()
                automod.loop.close()
            except:
                pass
            quit(1)