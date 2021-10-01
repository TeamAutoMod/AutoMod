import discord.http
discord.http.Route.BASE = "https://discordapp.com/api/v9"

import os
import json
import asyncio
import sentry_sdk
import datetime
import logging
import discordspy


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

        if bot.config.custom_status != "":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=bot.config.custom_status))

        log.info("Booted up & ready to go!")
    except Exception as ex:
        log.error("Failed to start - {}".format(ex))




if __name__ == "__main__":
    if not os.path.exists("./config.json"):
        print("Missing config file")
        exit(1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    config = json.load(open("./config.json", "r", encoding="utf8", errors="ignore", closefd=True))
    automod = AutoMod(config)
    if not automod.config.dev:
        discords = discordspy.Client(
            automod, 
            automod.config.discords_token, 
            post=discordspy.Post.auto()
        )
    automod.remove_command("help")

    with SetupLogging():
        log = logging.getLogger(__name__)
        try:
            for _s, s in ("SIGINT", "SIGTERM"):
                asyncio.get_event_loop().add_signal_handler(getattr(_s, s), lambda: asyncio.ensure_future(automod.close()))
        except Exception:
            pass

        loop.run_until_complete(boot(automod, log))

        @automod.event
        async def on_discords_server_post(
            status
        ):
            if status == 200:
                log.info(f"Posted server count ({discords.servers()}) on discords.com")
            else:
                log.info(f"Failed to post server count to discords.com - Status code {status}")

        automod.run()

        log.info("Shutting down...")