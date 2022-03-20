import discord

from ...types import Embed



class DMProcessor(object):
    def __init__(self, bot):
        self.bot = bot
        self.colors = {
            "kick": 0xf79554,
            "ban": 0xff5c5c,
            "mute": 0xffdc5c
        }

    
    async def execute(self, msg, _type, _user, _mod, _reason, **opt):
        try:
            e = Embed(
                color=self.color[_type],
                title=f"{msg.guild.name}",
                description=self.bot.locale.t(msg.guild, f"{_type}_dm", **opt)
            )
            e.add_fields([
                {
                    "name": "❯ Moderator",
                    "value": f"{_mod.name}#{_mod.discriminator}"
                },
                {
                    "name": "❯ Reason",
                    "value": f"{_reason}"
                }
            ])
            await _user.send(embed=e)
        except discord.Forbidden:
            pass