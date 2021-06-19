import React from 'react';
import { getUserInfo, getGuildRoles, getGuildChannels, getGuildConfig, getGuilds } from '../../utils/api';
import { DashboardComponent } from '../../components';



export function DashboardPage({history, match}) {

    const [user, setUser] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [config, setConfig] = React.useState({});
    const [roles, setRoles] = React.useState([]);
    const [channels, setChannels] = React.useState([]);
    const [guilds, setGuilds] = React.useState({});

    React.useEffect(() => {
        getUserInfo()
            .then(({data}) => {
                setUser(data)
            }).then(() => {
                return getGuildConfig(match.params.id);
            }).then(({data}) => {
                setConfig(data)
                return getGuildRoles(match.params.id);
            }).then(({data}) => {
                setRoles(data)
                return getGuildChannels(match.params.id)
            }).then(({data}) => {
                setChannels(data)
                setLoading(false);
            }).catch((err) => {
                console.log(err)
                history.push("/")
                setLoading(false)
            })
    }, [])

    return !loading && (
        <DashboardComponent config={config} roles={roles} channels={channels} user={user}/>
    )
}