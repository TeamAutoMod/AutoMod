import discord
from discord.ui import View

from .buttons import LinkBtn



class AboutView(View):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(LinkBtn(_url=f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=403041534&scope=bot+applications.commands", _label="Invite"))
        self.add_item(LinkBtn(_url=f"{bot.config.support_invite}", _label="Support"))
        self.add_item(LinkBtn(_url=f"https://top.gg/bot/{bot.user.id}/vote", _label="Top.gg"))
        self.add_item(LinkBtn(_url=f"https://discords.com/bots/bot/{bot.user.id}/vote", _label="discords.com"))