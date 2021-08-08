import React from 'react';
import { useRouter } from 'next/router';
import {fetchUserDeatils, fetchGuilds} from "../../utils/Api";



export default function Guilds() {
    const router = useRouter();
    const [user, setUser] = React.useState({discordId: "", discordTag: ""});
    const [loading, setLoading] = React.useState(true);
    const [guilds, setGuilds] = React.useState({excluded: [], included: []});

    React.useEffect(() => {
        fetchUserDeatils()
            .then(({data}) => {
                setUser(data);
                return fetchGuilds();
            }).then(({data}) => {
                setGuilds(data);
                setLoading(false);
            })
            .catch((error: Error) => {
                console.log(error);
                router.push("/login");
                setLoading(false)
            })
    }, [])

    return !loading && (
        <>
            <h1>Hey there, {user.discordTag}</h1>
            <ul>
                {guilds.included.map((g: any) => (
                    <li>{g.name}</li>
                ))}
            </ul>
        </>
    )
}