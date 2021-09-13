export interface Config {
    id: String;
    prefix: String;
    mute_role: String;
    
    mod_log: String;
    message_log: String;
    server_log: String;
    voice_log: String;

    antispam: Boolean;
    server_logging: Boolean;
    message_logging: Boolean;
    voice_logging: Boolean;
    persist: Boolean;
    dm_on_actions: Boolean;

    ignored_channels: Array<Number>;
    ignored_roles: Array<Number>;
    whitelisted_invites: Array<Number>;

    punishments: Object;

    automod: {
        invites: {warns: number}
        everyone: {warns: number}

        mention: {threshold: number}
        lines: {threshold: number}

        raid: {status: boolean, threshold: string}

        caps: {warns: number}
        files: {warns: number}
        zalgo: {warns: number}
        censor: {warns: number}
        spam: {status: boolean, warns: number}
    },

    filters: Object;

    embed_role: String;
    emoji_role: String;
    tag_role: String;

    cases: Number;
    case_ids: Object;

    lang: String;
    guild_name: String;
}