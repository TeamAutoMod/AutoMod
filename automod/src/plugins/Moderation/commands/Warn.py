from ..functions.WarnUser import warnUser
from ....utils import Permissions



async def run(plugin, ctx, user, reason):
    if reason is None:
        reason = plugin.translator.translate(ctx.guild, "no_reason")
    
    if not Permissions.is_allowed(ctx, ctx.author, user):
        return await ctx.send(plugin.translator.translate(ctx.guild, "warn_not_allowed", _emote="WARN"))
    
    await warnUser(plugin, ctx, user, reason)