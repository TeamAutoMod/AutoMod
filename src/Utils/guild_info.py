import time
from datetime import datetime

import discord


def guild_info_embed(guild):
    try:
        features = ", ".join(guild.features) if len(guild.features) > 0 else "None"
        created = guild.created_at.strftime("%d/%m/%Y")

        e = discord.Embed(color=0x6a7fc8)
        e.set_thumbnail(url=guild.icon_url_as())

        e.add_field(
            name="Server Information",
            value="```\n• ID: {} \n• Owner: {} \n• Created: {} \n• Features: {} \n```"\
            .format(
                guild.id, str(guild.owner), 
                f"{(datetime.fromtimestamp(time.time()) - guild.created_at).days} days ago ({created})",
                features
            ),
            inline=False
        )

        e.add_field(
            name="Stats",
            value="```\n• Roles: {} \n• Emojis: {} \n• Text: {} \n• Voice: {} \n```"\
            .format(
                len(guild.roles), 
                len(guild.emojis), 
                len(guild.text_channels), 
                len(guild.voice_channels)
            ),
            inline=False
        )
        
        e.add_field(
            name="Members",
            value="```\n• Total: {} \n• Users: {} \n• Bots: {} \n```"\
            .format(
                len(guild.members),
                len(list(filter(lambda m: not m.bot, guild.members))),
                len(list(filter(lambda m: m.bot, guild.members)))
            ),
            inline=False
        )

        if guild.splash_url != "":
            e.set_image(url=guild.splash_url)
        if guild.banner_url_as() != "":
            e.set_image(url=guild.banner_url_as())

        return e
    except Exception as ex:
        print(ex)