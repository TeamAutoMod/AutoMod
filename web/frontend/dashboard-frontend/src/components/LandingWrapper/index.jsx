import React from 'react';
import { Button } from '@chakra-ui/core';
import './landing.css';
import Logo from '../../assets/logo.png';


export function LandingComponent({loginStatus}) {
    const login = loginStatus === true ? "Dashboard" : "Login";
    const redirect = loginStatus === true ? "http://localhost:3000/menu" : "http://localhost:3001/api/auth/discord";
    const dashButton = () => window.location.href = `${redirect}`;
    const inviteButton = () => window.location.href = "https://discord.com/oauth2/authorize?client_id=697487580522086431&scope=bot&permissions=403041534";
    const docButton = () => window.location.href = "https://github.com/xezzz/AutoMod/wiki";
    return (
        <div className="landing">
            <div className="top">
                <div className="left">
                    <h1>
                        AutoMod
                    </h1>
                    <p>
                        AutoMod is a Discord moderation bot <br />for both large and small servers
                    </p>
                    <div className="buttons">
                        <ul>
                            <li>
                                <Button onClick={dashButton} className="btn">{login}</Button>
                            </li>
                            <li>
                                <Button onClick={inviteButton} className="btn">Invite</Button>
                            </li>
                        </ul>
                    </div>
                </div>
                <div className="right">
                    <img src={Logo} alt="logo" />
                </div>
            </div>
        </div>
    ) 
}