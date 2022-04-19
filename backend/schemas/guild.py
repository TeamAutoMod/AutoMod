def GuildConfig(guild, prefix):
    return {
        "id": f"{guild.id}", 
        "prefix": "{}".format(prefix if prefix != "" or prefix != None else "+"), 
        "mute_role": "",
        "mod_role": "",

        "mod_log": "", 
        "message_log": "",
        "server_log": "",
        "join_log": "",
        "member_log": "",

        "mod_log_webhook": "",
        "message_log_webhook": "",
        "server_log_webhook": "",
        "join_log_webhook": "",
        "member_log_webhook": "",

        "ignored_channels": [],
        "ignored_roles": [],
        "allowed_invites": [],
        "black_listed_links": [],
        "white_listed_links": [],
        "tags": {},

        "punishments": {},
        "automod": {},
        "filters": {},
        "regexes": {},
        "antispam": {
            "enabled": False,
            "rate": 0,
            "per": 0,
            "warns": 0,
        },
        
        "reaction_roles": {},

        "cases": 0,
        "case_ids": {},

        "pre_reasons": {},
        "lvl_sys": {
            "enabled": False,
            "notif_mode": "channel",
            "users": []
        },
        "disabled_commands": [],

        "lang": "en_US",
        "guild_name": f"{guild.name}",
}