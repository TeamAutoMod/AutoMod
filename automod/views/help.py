# type: ignore

import discord
from discord.ui import View, Select # pyright: reportMissingImports=false

from typing import List

from .buttons import LinkBtn



ACTUAL_PLUGIN_NAMES = {
    "ConfigPlugin": "<:aConfig:1054890378916016139> Configuration",
    "AutomodPlugin": "<:aMod:1054889663220949094> Automoderator",
    "ModerationPlugin": "<:aBan:1054889458446630942> Moderation",
    "FilterPlugin": "<:aDenied:1054890383340994650> Filters & Regexes",
    "UtilityPlugin": "<:aUtility:1054890965527179335> Utility",
    "LevelPlugin": "<:aTrophy:1054890963962703994> Level System",
    "TagsPlugin": "<:aCommand:1054890962989621259> Custom Commands & Responders",
    "CasesPlugin": "<:aCase:1054890959382528142> Case System",
    "ReactionRolesPlugin": "<:aRole:1054890960737288242> Reaction Roles"
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