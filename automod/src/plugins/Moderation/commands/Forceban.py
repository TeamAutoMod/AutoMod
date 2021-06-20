from discord.ext import commands

from ..functions.BanUser import banUser
from ....utils import Permissions



async def run(plugin, ctx, users, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")
    
    users = list(set(users))
    if len(users) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_member", _emote="WARN"))
    for user in users:
        if await Permissions.is_banned(ctx, user):
            await ctx.send(plugin.t(ctx.guild, "target_already_banned", _emote="WARN"))
        else:
            await banUser(plugin, ctx, user, reason, "forceban", "forcebanned")