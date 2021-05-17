from ..functions.MuteUser import muteUser
from ....utils import Permissions


async def run(plugin, ctx, user, length, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")
    
    if not Permissions.is_allowed(ctx, ctx.author, user):
        return await ctx.send(plugin.t(ctx.guild, "mute_not_allowed", _emote="WARN"))
    

    await muteUser(plugin, ctx, user, length, reason)