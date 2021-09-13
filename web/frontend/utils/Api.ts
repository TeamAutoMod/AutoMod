import axios from "axios";
const BASE_URL: String = "http://localhost:3001/api";



export function fetchUserDeatils() {
    return axios.get(BASE_URL + "/auth", {withCredentials: true});
};

export function fetchGuilds() {
    return axios.get(BASE_URL + "/discord/guilds", {withCredentials: true});
};

export function fetchGuildConfig(gid: any) {
    console.log(gid)
    return axios.get(BASE_URL + `/discord/guilds/${gid}/config`, {withCredentials: true});
}

export function fetchGuildRoles(gid: any) {
    console.log(gid)
    return axios.get(BASE_URL + `/discord/guilds/${gid}/roles`, {withCredentials: true});
}

export function fetchGuildChannels(gid: any) {
    console.log(gid)
    return axios.get(BASE_URL + `/discord/guilds/${gid}/channels`, {withCredentials: true});
}