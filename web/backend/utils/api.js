const fetch = require('node-fetch');
const { decrypt } = require('./utils');
const CryptoJS = require('crypto-js');
const OAuth2Credentials = require('../database/schemas/OAuth2Credentials');

DISCORD_API_BASE = "https://discord.com/api/v9"



async function fetchBotGuilds() {
    const response = await fetch(`${DISCORD_API_BASE}/users/@me/guilds`, {
        method: "GET",
        headers: {
            Authorization: `Bot ${process.env.BOT_TOKEN}`
        }
    });
    return response.json();
};

async function fetchUserGuilds(discordId) {
    const credentials = await OAuth2Credentials.findOne({discordId});
    if (!credentials) throw new Error("No credentials");
    const EncryptedAccessToken = credentials.get("access_token");
    const decrypted = decrypt(EncryptedAccessToken);
    const bearerToken = await decrypted.toString(CryptoJS.enc.Utf8);
    const response = await fetch(`${DISCORD_API_BASE}/users/@me/guilds`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${bearerToken}`
        }
    });
    return response.json();
}

async function fetchGuildRoles(guildId) {
    const response = await fetch(`${DISCORD_API_BASE}/guilds/${guildId}/roles`, {
        method: "GET",
        headers: {
            Authorization: `Bot ${process.env.BOT_TOKEN}`
        }
    })
    return response.json();
}

async function fetchGuildChannels(guildId) {
    const response = await fetch(`${DISCORD_API_BASE}/guilds/${guildId}/channels`, {
        method: "GET",
        headers: {
            Authorization: `Bot ${process.env.BOT_TOKEN}`
        }
    })
    return response.json();
}


module.exports = {fetchBotGuilds, fetchUserGuilds, fetchGuildRoles, fetchGuildChannels}