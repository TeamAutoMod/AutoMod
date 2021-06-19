const fetch = require('node-fetch');
const OAuth2Credentials = require('../database/schemas/OAuth2Credentials');
const { decrypt } = require('./utils')
const CryptoJS = require('crypto-js')

const BASE = "https://discord.com/api/v8";
const TOKEN = process.env.BOT_TOKEN;

async function getBotGuilds() {
    const res = await fetch(BASE + "/users/@me/guilds", {
        method: "GET",
        headers: {
            Authorization: `Bot ${TOKEN}`
        }
    })
    return res.json();
}

async function getUserGuilds(discordId) {
    const credentials = await OAuth2Credentials.findOne({discordId});
    if (!credentials) throw new Error("No credentials");
    const EncryptedAccessToken = credentials.get('access_token')
    const decrypted = decrypt(EncryptedAccessToken);
    const access = decrypted.toString(CryptoJS.enc.Utf8);
    const response = await fetch(`${BASE}/users/@me/guilds`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${access}`
        }
    })
    return response.json();
}


async function getGuildRoles(guildId) {
    const response = await fetch(`${BASE}/guilds/${guildId}/roles`, {
        method: "GET",
        headers: {
            Authorization: `Bot ${TOKEN}`
        }
    })
    return response.json();
}

async function getGuildChannels(guildId) {
    const response = await fetch(`${BASE}/guilds/${guildId}/channels`, {
        method: "GET",
        headers: {
            Authorization: `Bot ${TOKEN}`
        }
    })
    return response.json();
}


module.exports = {getBotGuilds, getUserGuilds, getGuildRoles, getGuildChannels}