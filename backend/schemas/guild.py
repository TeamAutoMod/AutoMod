


def GuildConfig(guild, prefix):
    return {
        "id": f"{guild.id}", 
        "prefix": "{}".format(prefix if prefix != "" or prefix != None else "!"), 
        "mute_role": "",

        "mod_log": "", 
        "message_log": "",
        "server_log": "",

        "ignored_channels": [],
        "ignored_roles": [],
        "whitelisted_invites": [],
        "tags": {},

        "punishments": {},
        "automod": {},
        "filters": {},

        "cases": 0,
        "case_ids": {},

        "pre_reasons": {},

        "lang": "en_US",
        "guild_name": f"{guild.name}",
    }