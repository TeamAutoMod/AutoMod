


def Slowmode(guild, channel, mod, time, pretty, mode):
    return {
        "id": f"{guild.id}-{channel.id}",
        "time": f"{time}",
        "pretty": pretty,
        "mode": mode,
        "mod": f"{mod.id}",
        "users": {}
    }