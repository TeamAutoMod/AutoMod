import logging
import traceback

from .Automod.AutomodPlugin import AutomodPlugin
from .Basic.BasicPlugin import BasicPlugin
from .Admin.AdminPlugin import AdminPlugin
from .Antispam.AntispamPlugin import AntispamPlugin
from .Moderation.ModerationPlugin import ModerationPlugin
from .Error.ErrorPlugin import ErrorPlugin
from .Selfroles.SelfrolesPlugin import SelfrolesPlugin
from .Cases.CasesPlugin import CasesPlugin
from .Config.ConfigPlugin import ConfigPlugin
from .Logs.LogsPlugin import LogsPlugin
from .Persist.PersistPlugin import PersistPlugin
from .LocateUser.LocateUserPlugin import LocateUserPlugin
from .Clean.CleanPlugin import CleanPlugin



log = logging.getLogger(__name__)

plugins = {
    # Plugin: Path
    # This also defines the order for the help command
    ErrorPlugin: "src.plugins.Error.ErrorPlugin",
    AutomodPlugin: "src.plugins.Automod.AutomodPlugin",
    BasicPlugin: "src.plugins.Basic.BasicPlugin",
    AdminPlugin: "src.plugins.Admin.AdminPlugin",
    AntispamPlugin: "src.plugins.Antispam.AntispamPlugin",
    ModerationPlugin: "src.plugins.Moderation.ModerationPlugin",
    ConfigPlugin: "src.plugins.Config.ConfigPlugin",
    SelfrolesPlugin: "src.plugins.Selfroles.SelfrolesPlugin",
    CasesPlugin: "src.plugins.Cases.CasesPlugin",
    PersistPlugin: "src.plugins.Persist.PersistPlugin",
    LogsPlugin: "src.plugins.Logs.LogsPlugin",
    LocateUserPlugin: "src.plugins.LocateUser.LocateUserPlugin",
    CleanPlugin: "src.plugins.Clean.CleanPlugin"
}


async def loadPlugins(bot):
    for plugin, path in plugins.items():
        try:
            plugin.set_path(plugin, path)
            bot.add_cog(plugin(bot))
            bot.load_extension(path)
        except Exception:
            ex = traceback.format_exc()
            log.warn("Failed to load plugin {} - {}".format(plugin, ex))