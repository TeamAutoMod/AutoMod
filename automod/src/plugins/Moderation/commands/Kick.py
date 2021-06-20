from discord.ext import commands

from ..functions.KickUser import kickUser
from ....utils import Permissions



async def run(plugin, ctx, users, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")

    users = list(set(users))
    if len(users) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_member", _emote="WARN"))
    for user in users:
        user = ctx.guild.get_member(user.id)
        if user is None:
            await ctx.send(plugin.t(ctx.guild, "target_not_on_server", _emote="WARN"))
        
        elif not Permissions.is_allowed(ctx, ctx.author, user):
            await ctx.send(plugin.t(ctx.guild, "kick_not_allowed", _emote="WARN"))
        
        elif await Permissions.is_banned(ctx, user):
            await ctx.send(plugin.t(ctx.guild, "target_already_banned", _emote="WARN"))
        else:
            await kickUser(plugin, ctx, user, reason)