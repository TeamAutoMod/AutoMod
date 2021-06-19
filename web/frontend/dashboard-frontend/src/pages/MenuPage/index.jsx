import React from 'react';
import { getUserInfo, getGuilds } from '../../utils/api';
import { MenuComponent } from '../../components';



export function MenuPage({history}) {

    const [user, setUser] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [guilds, setGuilds] = React.useState({});

    React.useEffect(() => {
        getUserInfo()
            .then(({data}) => {
                setUser(data)
                return getGuilds()
            }).then(({data}) => {
                setGuilds(data)
                setLoading(false)
            }).catch((err) => {
                history.push("/")
                setLoading(false)
            })
    }, [])

    return !loading && (
        <MenuComponent guilds={guilds} user={user}/>
    )
}