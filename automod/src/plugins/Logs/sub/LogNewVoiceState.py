from ...Types import Embed



async def logNewVoiceState(plugin, guild, member, before, after):
    _type = "voice_"
    kwargs = {}
    
    if before.channel is None and after.channel is not None:
        _type += "join"
        kwargs.update({
           "color": 0x5cff9d,
            "description": f"**{member}** joined voice channel **{after.channel}**"
        })
    elif before.channel is not None and after.channel is None:
        _type += "join"
        kwargs.update({
           "color": 0xff5c5c,
            "description": f"**{member}** left voice channel **{before.channel}**"
        })
    elif before.channel is not None and after.channel is not None and before.channel is not after.channel:
        _type += "join"
        kwargs.update({
            "color": 0xffdc5c,
            "description": f"**{member}** moved from voice channel **{before.channel}** to **{after.channel}**"
        })
    else:
        return
    
    e = Embed(**kwargs)
    await plugin.action_logger.log(
        guild, 
        _type, 
        _embed=e
    )