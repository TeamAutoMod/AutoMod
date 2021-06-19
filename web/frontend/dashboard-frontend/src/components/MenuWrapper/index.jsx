import React from 'react';
import { Link } from 'react-router-dom';
import './menu.css';


export function MenuComponent({guilds, user}) {
    return (
        <div className="menu">
            <div className="top">
                <div className="text">
                    <h1>
                        Hey there, {user.discordTag.slice(0, -5)}!
                    </h1>
                </div>
                <div className="selection">
                    <ul>
                        {guilds.included.map((guild) => (
                            <li>
                                <div className="g">
                                    <img src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`} alt="guild-icon" />
                                    <h1>
                                        {guild.name}
                                    </h1>
                                    <Link to={`/dashboard/${guild.id}`} style={{border: "none"}}>
                                        <p>Dashboard</p>
                                    </Link>
                                </div>
                            </li>
                        ))}
                        <li>
                            <div className="g">
                                <img src={`https://www.freeiconspng.com/thumbs/plus-icon/plus-icon-black-2.png`} alt="guild-icon" />
                                <h1>
                                    Add to new server
                                </h1>
                                <a href={"https://discord.com/oauth2/authorize?client_id=697487580522086431&scope=bot&permissions=403041534"}>
                                    <p style={{background: "green", border: "none"}}>Invite</p>
                                </a>
                            </div>
                        </li>

                    </ul>
                </div>
            </div>
        </div>
    )
}