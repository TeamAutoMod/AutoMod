


async def logNewVoiceState(plugin, guild, member, before, after):
    _type = "voice_"
    kwargs = {
        "user": member
    }
    
    if before.channel is None and after.channel is not None:
        _type += "join"
        kwargs.update({
            "afterChannel": after.channel
        })
    elif before.channel is not None and after.channel is None:
        _type += "join"
        kwargs.update({
            "beforeChannel": before.channel
        })
    elif before.channel is not None and after.channel is not None and before.channel is not after.channel:
        _type += "join"
        kwargs.update({
            "beforeChannel": before.channel,
            "afterChannel": after.channel
        })
    else:
        return
    
    await plugin.action_logger.log(guild, _type, **kwargs)