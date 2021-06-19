import React from 'react';
import { LandingComponent } from '../../components';
import { getUserInfo } from '../../utils/api';



export function LandingPage(props) {

    const [user, setUser] = React.useState(null);
    const [loginStatus, setLoginStatus] = React.useState(false);

    React.useEffect(() => {
        getUserInfo()
            .then(({data}) => {
                setUser(data)
                setLoginStatus(true)
            }).catch((err) => {
                setLoginStatus(false)
            })
    }, [])
    
    return (
        <LandingComponent loginStatus={loginStatus} />
    )
}