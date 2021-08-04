from discord.ext import commands

from ..sub.UnbanUser import unbanUser



async def run(plugin, ctx, user, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")
    await unbanUser(plugin, ctx, user, reason)