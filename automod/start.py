import discord.http
discord.http.Route.BASE = "https://discordapp.com/api/v6"

import os
import json
import asyncio
import sentry_sdk


from src import AutoMod
from src.logger import SetupLogging



def run(bot):
    sentry_sdk.init(
<<<<<<< HEAD
        bot.config.sentry_dsn,
=======
        bot.config["sentry_dsn"],
>>>>>>> f40ed3caff6b455cf03f56d37f925532425549d2
        traces_sample_rate=1.0
    )
    bot.remove_command("help")
    bot.run()


if __name__ == "__main__":
    if not os.path.exists("./config.json"):
        print("Missing config file")
        exit(1)

    config = json.load(open("./config.json", "r", closefd=True))
    automod = AutoMod(config)

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