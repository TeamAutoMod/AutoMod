import discord

from ...Types import Embed
from ....utils.Views import AboutView



async def run(plugin, ctx):
    bot = plugin.bot
    e = Embed(
        title="AutoMod",
        description=plugin.i18next.t(ctx.guild, "about_text")
    )
    e.set_thumbnail(url=plugin.bot.user.avatar.with_size(1024))

    view = AboutView()
    await ctx.send(embed=e, view=view)
