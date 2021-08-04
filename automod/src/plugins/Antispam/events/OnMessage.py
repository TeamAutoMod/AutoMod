from ..sub.CheckMessage import checkMessage



async def run(plugin, message):
    if message.guild is None:
        return
    if plugin.db.configs.get(message.guild.id, "antispam") is False:
        return


    await checkMessage(plugin, message)