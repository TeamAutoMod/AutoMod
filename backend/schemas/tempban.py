


def Tempban(guild_id, user_id, until):
    return {
        "id": f"{guild_id}-{user_id}",
        "until": until
    }