from ..sub.MuteUser import muteUser
from ....utils import Permissions



async def run(plugin, ctx, user, length, reason):
    if reason is None:
        reason = plugin.i18next.t(ctx.guild, "no_reason")
    
    if not Permissions.is_allowed(ctx, ctx.author, user):
        return await ctx.send(plugin.i18next.t(ctx.guild, "mute_not_allowed", _emote="NO"))
    

    await muteUser(plugin, ctx, user, length, reason)