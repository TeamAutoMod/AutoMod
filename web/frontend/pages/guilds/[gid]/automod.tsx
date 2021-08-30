import { useRouter } from "next/router";
import styles from '../../../styles/Automod.module.css';
import React from 'react';
import { fetchUserDeatils, fetchGuildConfig, fetchGuildRoles, fetchGuildChannels } from '../../../utils/Api';
import { Config } from '../../types/Config';
// import { AutomodPlugin } from '../../components/AutomodPlugin';




export default function Automod() {
    const router = useRouter();
    console.log(router.query)
    const { gid } = router.query;

    const [user, setUser] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [config, setConfig] = React.useState<Config>();
    const [roles, setRoles] = React.useState([]);
    const [channels, setChannels] = React.useState([]);

    React.useEffect(() => {
        if(!router.isReady) return;
        fetchUserDeatils()
            .then(({data}) => {
                setUser(data);
                return fetchGuildConfig(gid)
            })
            .then(({data}) => {
                setConfig(data);
                return fetchGuildRoles(gid)
            })
            .then(({data}) => {
                setRoles(data)
                return fetchGuildChannels(gid)
            })
            .then(({data}) => {
                setChannels(data)
                setLoading(false)
            })
            .catch((error: Error) => {
                console.log(error);
                router.push("/login");
                setLoading(false)
            })
    }, [router.isReady])

    return !loading && (
        <div className={styles.guild_container}>
            <div className={styles.text}>
                <h1>Automoderator - {config?.guild_name}</h1>
            </div>

            {/* <div className={styles.ignore_section}>
                <ul>
                    <h1>Ignore Roles</h1>
                    <p>Users with these roles will be ignored by the automoderator.</p>
                    <Field
                        component={SelectField}
                        name="Roles"
                        options={roles}
                    />
                </ul>
            </div> */}
        </div>
    )
}