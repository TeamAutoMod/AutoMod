import React from 'react';
import { useRouter } from 'next/router';
import { fetchUserDeatils, fetchGuilds } from "../../utils/Api";
import { Guild } from "../types/Guild";
import styles from '../../styles/Guilds.module.css';
import { GuildCard } from '../components/GuildCard';



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
            })
            .then(({data}) => {
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
        <div className={styles.guild_container}>
            <div className={styles.test}>
                <div className={styles.text}>
                    <h1>
                        Choose one of your servers, {user.discordTag.slice(0 ,user.discordTag.length - 5)}
                    </h1>
                </div>
                <div className={styles.guilds}>
                    <ul>
                        {guilds.included.map((g: Guild) => (
                            <GuildCard guild={g} manage={true}/>
                        ))}
                        {guilds.excluded.map((g: Guild) => (
                            <GuildCard guild={g} manage={false}/>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    )
}