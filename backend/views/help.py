import discord
from discord.ui import View # pyright: reportMissingImports=false

from .buttons import LinkBtn



class HelpView(View):
    def __init__(
        self, 
        bot, 
        show_invite: bool = False, 
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(LinkBtn(_url=f"{bot.config.support_invite}", _label="Support"))
        self.add_item(LinkBtn(_url=f"https://top.gg/bot/{bot.user.id}/vote", _label="Vote"))
        
        if show_invite == True:
            self.add_item(LinkBtn(_url=f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=403041534&scope=bot+applications.commands", _label="Invite"))