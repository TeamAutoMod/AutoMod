from discord.ext import commands

from ..functions.UnbanUser import unbanUser



async def run(plugin, ctx, user, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")
    else:
        await unbanUser(plugin, ctx, user, reason)