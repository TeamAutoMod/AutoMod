from discord.ext import commands

from ..sub.BanUser import banUser
from ....utils import Permissions



async def run(plugin, ctx, users, reason):
    if reason is None:
        reason = plugin.i18next.t(ctx.guild, "no_reason")
    
    users = list(set(users))
    if len(users) < 1:
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_member", _emote="NO"))
    for user in users:
        await banUser(plugin, ctx, user, reason, "forceban", "forcebanned")
