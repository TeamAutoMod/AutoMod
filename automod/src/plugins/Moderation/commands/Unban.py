from discord.ext import commands

from ..functions.UnbanUser import unbanUser
from ....utils import Permissions



async def run(plugin, ctx, user, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")
    
    if not await Permissions.is_banned(ctx, user):
        await ctx.send(plugin.t(ctx.guild, "target_not_banned", _emote="WARN"))
    else:
        await unbanUser(plugin, ctx, user, reason)