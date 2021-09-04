


async def run(plugin, channel):
    plugin.bot.cache.text_channels[channel.guild.id] = channel.guild.text_channels
    plugin.bot.cache.voice_channels[channel.guild.id] = channel.guild.voice_channels