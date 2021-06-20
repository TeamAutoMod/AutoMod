import importlib
import logging
import traceback

from Bot import Reload, Handlers
from Utils import Logging, Utils



log = logging.getLogger(__name__)


async def _reload(admin, bot):
    try:
        log.info(f"[Hot Reload] Hot reload triggered by {admin}")
        await Utils.perform_shell_code("git pull origin master")

        importlib.reload(Reload)
        log.info("[Hot Reload] Reloading components")

        for component in Reload.components:
            importlib.reload(component)
            log.info(f"[Hot Reload] Reloaded component {component}")
        
        await Logging.init(bot)

        log.info("[Hot Reload] Reloading cogs")
        temp = []
        for cog in bot.cogs:
            temp.append(cog)
        for cog in temp:
            bot.unload_extension("Plugins.%s" % (cog))
            log.info(f"[Hot Reload] Unloaded module {cog}")
            bot.load_extension("Plugins.%s" % (cog))
            log.info(f"[Hot Reload] Loaded module {cog}")
            
        log.info("[Hot Reload] Calling init_bot() method from Handlers file")
        await Handlers.init_bot(bot)

        _version = await Utils.get_version()
        bot.version = _version
        log.info(f"[Hot Reload] Hot reload completed, now running on version {_version}")
    except Exception:
        traceback.print_exc()