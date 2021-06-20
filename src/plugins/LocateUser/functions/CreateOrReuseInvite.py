


async def createOrReuseInvite(plugin, ctx, user):
    vc = user.voice.channel

    invites = await vc.invites()
    if len(invites) > 0:
        return invites[0]
    else:
        return await vc.create_invite()