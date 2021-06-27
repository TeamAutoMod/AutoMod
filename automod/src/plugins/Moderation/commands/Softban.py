from discord.ext import commands

from ..functions.BanUser import banUser
from ..functions.UnbanUser import unbanUser
from ....utils import Permissions



async def run(plugin, ctx, users, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")

    users = list(set(users))
    if len(users) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_member", _emote="NO"))
    for user in users:
        user = ctx.guild.get_member(user.id)
        if user is None:
            await ctx.send(plugin.t(ctx.guild, "target_not_on_server", _emote="NO"))
        
        elif not Permissions.is_allowed(ctx, ctx.author, user):
            await ctx.send(plugin.t(ctx.guild, "ban_not_allowed", _emote="NO"))
        else:
            await banUser(plugin, ctx, user, reason, "softban", "softbanned", days=7)
            await unbanUser(plugin, ctx, user, "Softban")