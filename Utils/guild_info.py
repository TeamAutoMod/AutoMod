import time
from datetime import datetime

import discord


def guild_info_embed(guild):
    features = ", ".join(guild.features)
    if features == "":
        features = None
    created = guild.created_at.strftime("%d/%m/%Y")
    e = discord.Embed(color=discord.Color.blurple())
    e.set_thumbnail(url=guild.icon_url_as())
    e.add_field(name="Name", value=guild.name, inline=True)
    e.add_field(name="ID", value=guild.id, inline=True)
    e.add_field(name="Owner", value=guild.owner, inline=True)
    e.add_field(name="Members", value="Total: {} \nUsers: {} \nBots: {}".format(len(guild.members), len([x for x in guild.members if x.bot is False]), len([x for x in guild.members if x.bot is True])), inline=True)

    e.add_field(
        name="**Channels**",
        value=f"📚 Categories: {str(len(guild.categories))} \n💬 Text: {str(len(guild.text_channels))} \n🔊 Voice: {str(len(guild.voice_channels))}",
        inline=True
    )
    e.add_field(
        name="**Created**",
        value=f"{created} ({(datetime.fromtimestamp(time.time()) - guild.created_at).days} days ago)",
        inline=True
    )
    e.add_field(
        name="**Features**",
        value=features,
        inline=True
    )
    if guild.icon_url_as() != "":
        e.add_field(
            name="**Icon**",
            value=f"[Icon]({guild.icon_url_as()})",
            inline=True
        )
    roles = ", ".join(r.mention for r in guild.roles if r != guild.default_role)
    e.add_field(
        name="**Roles**",
        value=roles if len(roles) < 1000 else f"{len(guild.roles)} roles",
        inline=False
    )

    if guild.emojis:
        emojis = "".join(str(emoji) for emoji in guild.emojis)
        e.add_field(
            name="**Emojis**",
            value=emojis if len(emojis) < 1024 else f"{len(guild.emojis)}"
        )

    if guild.splash_url != "":
        e.set_image(url=guild.splash_url)
    if guild.banner_url_as() != "":
        e.set_image(url=guild.banner_url_as())

    return e
