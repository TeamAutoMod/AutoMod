import axios from 'axios';

const BASE = "http://localhost:3001/api"


export function getUserInfo() {
    return axios.get(BASE + "/auth", {withCredentials: true})
}

export function getGuilds() {
    return axios.get(BASE + "/discord/guilds", {withCredentials: true})
}

export function getGuildConfig(guildId) {
    return axios.get(BASE + `/discord/guilds/${guildId}/config`, {withCredentials: true})
}

export function getGuildRoles(guildId) {
    return axios.get(BASE + `/discord/guilds/${guildId}/roles`, {withCredentials: true})
}

export function getGuildChannels(guildId) {
    return axios.get(BASE + `/discord/guilds/${guildId}/channels`, {withCredentials: true})
}