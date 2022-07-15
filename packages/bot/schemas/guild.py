import discord



def GuildConfig(
    guild: discord.Guild, 
    prefix: str
) -> dict:
    return {
        "id": f"{guild.id}", 
        "prefix": "{}".format(prefix if prefix != "" or prefix != None else "+"), 
        "mute_role": "",
        "mod_role": "",
        "join_role": "",

        "mod_log": "", 
        "message_log": "",
        "server_log": "",
        "join_log": "",
        "member_log": "",
        "voice_log": "",
        "report_log": "",

        "mod_log_webhook": "",
        "message_log_webhook": "",
        "server_log_webhook": "",
        "join_log_webhook": "",
        "member_log_webhook": "",
        "voice_log_webhook": "",
        "report_log_webhook": "",

        "ignored_channels_automod": [],
        "ignored_roles_automod": [],
        "ignored_channels_log": [],
        "ignored_roles_log": [],

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
        "raid_config": {
            "enabled": True
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