# type: ignore

import discord
from discord.ui import View, Select # pyright: reportMissingImports=false

from .buttons import LinkBtn



ACTUAL_PLUGIN_NAMES = {
    "ConfigPlugin": "Configuration",
    "AutomodPlugin": "Automoderator",
    "ModerationPlugin": "Moderation",
    "FilterPlugin": "Filters & Regexes",
    "UtilityPlugin": "Utility",
    "LevelPlugin": "Level System",
    "TagsPlugin": "Custom Commands & Responders",
    "CasesPlugin": "Case System",
    "ReactionRolesPlugin": "Reaction Roles"
    #"AlertsPlugin": "👾 Twitch Alerts"
}


class HelpView(View):
    def __init__(
        self, 
        bot, 
        show_buttons: bool = False,
        viewable_plugins: list = [],
        *args, 
        **kwargs
    ) -> None:
        self.bot = bot
        super().__init__(*args, **kwargs)

        if show_buttons == False:
            self.add_item(
                Select(
                    placeholder="Select a plugin",
                    options=[
                        discord.SelectOption(
                            label=v,
                            value=k
                        ) for k, v in ACTUAL_PLUGIN_NAMES.items() if k in viewable_plugins
                    ],
                    custom_id="help-select"
                )
            )
        else:
            self.add_item(LinkBtn(_url=f"{bot.config.support_invite}", _label="Support"))
            self.add_item(LinkBtn(_url=f"https://top.gg/bot/{bot.user.id}/vote", _label="Vote"))