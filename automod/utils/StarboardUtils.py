import discord

from typing import Tuple
import re

from plugins.Types import Embed



def get_star_emoji(stars: int) -> str:
    if 5 > stars >= 0:
        return "⭐"
    elif 10 > stars >= 5:
        return "🌟"
    elif 25 > stars >= 10:
        return "💫"
    else:
        return "✨"


def spoiler(content, url):
    s = re.compile(r'\|\|(.+?)\|\|').findall(content)
    for sp in s:
        if url in sp:
            return True
    return False


def get_stars_for_message(plugin, message: discord.Message) -> Tuple[int, bool]:
    _id = f"{message.id}"
    if not plugin.db.stars.exists(_id):
        plugin.db.stars.insert(plugin.schemas.StarboardEntry(message))
        return 1, True
    else:
        stars = plugin.db.stars.get(_id, "stars")
        new = stars + 1
        plugin.db.stars.update(_id, "stars", new)
        return new, False



def build_embed(message: discord.Message, stars: int) -> Tuple[Embed, str]:
    star_emoji = get_star_emoji(stars)
    content = f"{star_emoji} **{stars}**"

    embed = Embed(
        description=message.content
    )
    embed.set_author(
        name=f"{message.author.name}#{message.author.discriminator}",
        icon_url=message.author.display_avatar
    )

    if message.embeds:
        e = message.embeds[0]
        if e.type == "image" and not spoiler(message.content, e.url):
            embed.set_image(url=e.url)

    if message.attachments:
        file = message.attachments[0]
        is_spoiler = file.is_spoiler()
        if not is_spoiler and file.url.lower().endswith(("png", "jpg", "jpeg", "gif", "webp")):
            embed.set_image(url=file.url)
        elif is_spoiler:
            embed.add_field(
                name="❯ Attachment",
                value=f"||[{file.filename}]({file.url})||"
            )
        else:
            embed.add_field(
                name="❯ Attachment",
                value=f"[{file.filename}]({file.url})"
            )

    embed.add_field(
        name="❯ Original message",
        value=f"[Here!]({message.jump_url})"
    )
    embed.set_footer(
        text=f"#{message.channel.name}"
    )

    return embed, content


async def edit_or_send(plugin, new, message, channel, content, embed):
    if new:
        msg = await channel.send(
            content=content,
            embed=embed
        )
        plugin.db.stars.update(f"{message.id}", "log_message", f"{msg.id}")
    else:
        msg_id = plugin.db.stars.get(f"{message.id}", "log_message")
        msg = await channel.fetch_message(int(msg_id))
        if msg == None:
            return
        await msg.edit(
            allowed_mentions=discord.AllowedMentions(replied_user=False), 
            content=content,
            embed=embed
        )


async def delete_or_edit(plugin, message, channel):
    stars = plugin.db.stars.get(f"{message.id}", "stars")
    new = stars - 1

    log_message_id = plugin.db.stars.get(f"{message.id}", "log_message")
    log_message = await channel.fetch_message(int(log_message_id))
    if log_message != None:
        if new <= 0:
            await log_message.delete()
        else:
            star_emoji = get_star_emoji(new)
            await log_message.edit(
                content=f"{star_emoji} **{new}**"
            )
    if new <= 0:
        plugin.db.stars.delete(f"{message.id}")
    else:
        plugin.db.stars.update(f"{message.id}", "stars", new)
    


