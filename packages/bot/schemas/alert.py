# type: ignore

import discord



def Alert(
    streamer: str,
    guild: discord.Guild,
    channel: discord.TextChannel
) -> dict:
    return {
        "id": f"{streamer.lower()}",
        "in": {
            f"{guild.id}": f"{channel.id}"
        }
    }