from ....utils import Permissions



async def checkMessage(plugin, message):
    if Permissions.is_mod(message.author) or message.author.discriminator == "0000" or message.author.id == plugin.bot.user.id:
        return

    if message.author.id in plugin.is_being_handled:
        return

    if not "spam" in plugin.db.configs.get(message.guild.id, "automod"):
        return

    if plugin.db.configs.get(message.guild.id, "automod")["spam"]["status"] is False:
        return
    
    c = plugin.spam_checker[message.guild.id]
    if not c.is_spamming(message):
        return
    
    plugin.is_being_handled.append(message.author.id)

    await plugin.action_validator.figure_it_out(
        message, 
        message.author,
        "spam",
        moderator=plugin.bot.user,
        moderator_id=plugin.bot.user.id,
        user=message.author,
        user_id=message.author.id,
        reason="Spamming messages"
    )
    plugin.is_being_handled.remove(message.author.id)