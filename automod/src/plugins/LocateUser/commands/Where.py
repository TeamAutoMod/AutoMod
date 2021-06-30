from ..functions.CreateOrReuseInvite import createOrReuseInvite



async def run(plugin, ctx, user):
    if user.voice is None:
        return await ctx.send(plugin.t(ctx.guild, "not_in_voice", _emote="NO"))

    try:
        invite = await createOrReuseInvite(plugin, ctx, user)
    except Exception as ex:
        return await ctx.send(plugin.t(ctx.guild, "error_invite", _emote="NO", exc=ex))
    else:
        return await ctx.send(plugin.t(ctx.guild, "send_where", user=user, channel=user.voice.channel, invite=invite))
    