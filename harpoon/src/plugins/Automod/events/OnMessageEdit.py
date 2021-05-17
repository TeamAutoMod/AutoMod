from ..functions.CheckMessage import checkMessage


async def run(plugin, before, after):
    if after.guild is None:
        return
    if not plugin.db.configs.get(after.guild.id, "automod"):
        return
    
    if before.content != after.content and after.content == None:
        return
    
    await checkMessage(plugin, after)