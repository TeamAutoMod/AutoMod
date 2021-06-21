import discord



allowed_file_formats = [
    # plain text/markdown
    "txt",
    "md",

    # image
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",

    # video
    "mov",
    "mp4",
    "flv",
    "mkv",

    # audio
    "mp3",
    "wav",
    "m4a"
]

async def check(plugin, message):
    if len(message.attachments) > 0 and "files" in plugin.db.configs.get(message.guild.id, "automod"):
        attachments = {x: x.url.split(".")[-1] for x in message.attachments}
        unallowed = [k for k, v in attachments.items() if v.lower() not in allowed_file_formats]
        if len(unallowed) > 0:
            try:
                await message.delete()
            except Exception:
                pass
            forbidden = [x.filename for x in unallowed]
            plugin.bot.ignore_for_event.add("messages", message.id)

            await plugin.action_validator.figure_it_out(
                message, 
                message.author,
                "files",
                moderator=plugin.bot.user,
                moderator_id=plugin.bot.user.id,
                user=message.author,
                user_id=message.author.id,  
                reason=f"Sending forbidden attachment type (Was not plain/rich text, Markdown, or common image/video format): {', '.join(forbidden)}"
            )