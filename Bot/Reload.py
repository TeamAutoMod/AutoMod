from Utils import Constants, Context, Converters, Generators, guild_info, \
    Logging, Matchers, Pages, PermCheckers, Reload, Utils
from i18n import Translator
from Bot import Handlers
from Cogs import Base
from Database import Connector, DBUtils, Schemas


components = [
    DBUtils,
    Schemas,
    Connector,
    Logging,
    Constants,
    Context,
    Converters,
    Generators,
    guild_info,
    Logging,
    Matchers,
    Pages,
    PermCheckers,
    Reload,
    Utils,
    Base,
    Translator,
    Handlers
]