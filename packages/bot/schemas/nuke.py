import datetime



def Nuke(
    guild_id: int,
    channel_id: int,
    until: datetime.datetime,
    timeout: datetime.datetime,
    phrase: str
) -> dict:
    return {
        "id": f"{guild_id}-{channel_id}",
        "guild": f"{guild_id}",
        "channel": f"{channel_id}",
        "until": until,
        "timeout": timeout,
        "phrase": phrase
    }