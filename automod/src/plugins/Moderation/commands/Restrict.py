from ..functions.RestrictUser import restrictUser
from ....utils import Permissions



async def run(plugin, ctx, restriction, user, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")
    
    if not Permissions.is_allowed(ctx, ctx.author, user):
        return await ctx.send(plugin.t(ctx.guild, "restrict_not_allowed", _emote="NO"))

    await restrictUser(plugin, ctx, restriction, user, reason)