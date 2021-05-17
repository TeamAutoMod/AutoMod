from ..functions.CheckMessage import checkMessage


async def run(plugin, message):
    if message.guild is None:
        return
    if not plugin.db.configs.get(message.guild.id, "automod"):
        return

    await checkMessage(plugin, message)
