import datetime



def Mute(guild_id: int, user_id: int, until: datetime.datetime) -> dict:
    return {
        "id": f"{guild_id}-{user_id}",
        "until": until
    }