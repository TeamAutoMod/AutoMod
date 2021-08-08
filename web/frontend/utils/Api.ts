import axios from "axios";
const BASE_URL: String = "http://localhost:3001/api";



export function fetchUserDeatils() {
    return axios.get(BASE_URL + "/auth", {withCredentials: true});
};

export function fetchGuilds() {
    return axios.get(BASE_URL + "/discord/guilds", {withCredentials: true});
};