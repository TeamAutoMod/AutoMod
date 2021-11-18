import discord.http; discord.http.Route.BASE = "https://discordapp.com/api/v9"

import os
import json
import asyncio
import sentry_sdk
import datetime
import logging

from bot.AutoMod import AutoMod
from bot.logger import SetupLogging



async def boot(bot, log):
    try:
        version = bot.version = await bot.utils.getVersion()
        log.info("Spinning up version {}".format(version))

        sentry_sdk.init(
            bot.config.sentry_dsn,
            traces_sample_rate=1.0
        )

        if not hasattr(bot, "uptime"):
            bot.uptime = datetime.datetime.utcnow()
        
        for plugin in bot.config.plugins:
            try:
                bot.load_extension("plugins.{}".format(plugin))
                log.info("Loaded {}".format(plugin))
            except Exception as ex:
                log.warning("Failed to load {} - {}".format(plugin, ex))

        bot.ready = True
        bot.locked = False

        log.info("Booted up & ready to go!")
    except Exception as ex:
        log.error("Failed to start - {}".format(ex))




if __name__ == "__main__":
    if not os.path.exists("./config.json"):
        print("Missing config file")
        exit(1)

    config = json.load(open("./config.json", "r", encoding="utf8", errors="ignore", closefd=True))
    automod = AutoMod(config)
    
    automod.remove_command("help")

    with SetupLogging():
        log = logging.getLogger(__name__)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            for _s, s in ("SIGINT", "SIGTERM"):
                asyncio.get_event_loop().add_signal_handler(getattr(_s, s), lambda: asyncio.ensure_future(automod.close()))
        except Exception:
            pass

        loop.run_until_complete(boot(automod, log))

        automod.run()

        log.info("Shutting down...")