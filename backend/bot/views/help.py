# type: ignore

import discord
from discord.ui import View, Select # pyright: reportMissingImports=false

from typing import List

from .buttons import LinkBtn



ACTUAL_PLUGIN_NAMES = {
    "ConfigPlugin": "<:aConfig:1050619162889814086> Configuration",
    "AutomodPlugin": "<:aMod:1050607461272399964> Automoderator",
    "ModerationPlugin": "<:aBan:1050607129075142656> Moderation",
    "FilterPlugin": "<:aNoEntry:1050607297719701615> Filters & Regexes",
    "UtilityPlugin": "<:aUtility:1050609494448672808> Utility",
    "LevelPlugin": "<:aLevel:1050609493223944252> Level System",
    "TagsPlugin": "<:aCommands:1050609491974033469> Custom Commands & Responders",
    "CasesPlugin": "<:aCase:1050609490678009927> Case System",
    "ReactionRolesPlugin": "<:aRoles:1050609489532964934> Reaction Roles"
}


class HelpView(View):
    def __init__(self, bot, show_buttons: bool = False, viewable_plugins: List[str] = [], current_select: str = None, *args, **kwargs) -> None:
        self.bot = bot
        super().__init__(
            *args,
            **kwargs
        )

        if show_buttons == False:
            self.add_item(
                Select(
                    placeholder="Select Plugin",
                    options=[
                        discord.SelectOption(
                            label=" ".join(v.split(" ")[1:]),
                            emoji=v.split(" ")[0],
                            value=k,
                            default=False if current_select == None else True if current_select.lower() == k.lower() else False
                        ) for k, v in ACTUAL_PLUGIN_NAMES.items() if k in viewable_plugins
                    ],
                    custom_id="help-select"
                )
            )
        else:
            self.add_item(LinkBtn(_url=f"{bot.config.support_invite}", _label="Support"))
            self.add_item(LinkBtn(_url=f"https://top.gg/bot/{bot.user.id}/vote", _label="Vote"))