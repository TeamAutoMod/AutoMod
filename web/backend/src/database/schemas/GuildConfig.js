const mongoose = require('mongoose');

const GuildConfigSchema = new mongoose.Schema({
    id: {
        type: String,
        required: true,
        unique: true
    },
    prefix: {
        type: String,
        required: true,
    },
    mute_role: {
        type: String,
        required: false,
    },

    mod_log: {
        type: String,
        required: false,
    },
    message_log: {
        type: String,
        required: false,
    },
    server_log: {
        type: String,
        required: false,
    },
    voice_log: {
        type: String,
        required: false,
    },

    antispam: {
        type: Boolean,
        required: true,
        default: false
    },
    server_logging: {
        type: Boolean,
        required: true,
        default: false
    },
    message_logging: {
        type: Boolean,
        required: true,
        default: false
    },
    voice_logging: {
        type: Boolean,
        required: true,
        default: false
    },
    persist: {
        type: Boolean,
        required: true,
        default: false
    },
    dm_on_actions: {
        type: Boolean,
        required: true,
        default: false
    },

    ignored_channels: {
        type: Array,
        required: true,
        default: []
    },
    ignored_roles: {
        type: Array,
        required: true,
        default: []
    },
    whitelisted_invites: {
        type: Array,
        required: true,
        default: []
    },

    punishments: {
        type: Object,
        required: true,
        default: {}
    },
    automod: {
        type: Object,
        required: true,
        default: {}
    },
    filters: {
        type: Object,
        required: true,
        default: {}
    },

    lang: {
        type: String,
        required: true,
        default: "en_US"
    },
    cases: {
        type: Number,
        required: true,
        default: 0
    },
    guild_name: {
        type: String,
        required: true
    }
});

module.exports = mongoose.model("GuildConfig", GuildConfigSchema);