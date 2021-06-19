from ..functions.LogNewVoiceState import logNewVoiceState



async def run(plugin, member, before, after):
    guild = member.guild
    if guild is None:
        return
    
    if plugin.db.configs.get(guild.id, "voice_logging") is False:
        return

    await logNewVoiceState(plugin, guild, member, before, after)