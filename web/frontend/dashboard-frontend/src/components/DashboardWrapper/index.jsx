import React from 'react';
import { ConfigModal } from './Modals';
import './dashboard.css';



export function DashboardComponent({config, roles, channels, user}) {
    React.useEffect(() => {
        const timer = setTimeout(() => {
            const modal = document.getElementsByClassName("modal")[0];
            const btn = document.getElementsByClassName("openModal")[0];
            const span = document.getElementsByClassName("close")[0];
            const modules = document.getElementsByClassName("modules")[0];

            btn.onclick = function() {
                modal.style.display = "block";
                modules.style.opacity = "0.2"
            }

            span.onclick = function() {
                modal.style.display = "none"
                modules.style.opacity = "1"
            }

            window.onclick = function(event) {
                if (event.target === modal) {
                    modal.style.display = "none"
                    modules.style.opacity = "1"
                }
            }
        }, 500)
        return () => {
            clearTimeout(timer)
        }
    }, [])
    return (
        <div className="dashboard">
            <div className="dashboard-top">
                <div className="dashboard-text">
                    <h1>
                        Dashboard for {config.guild_name}
                    </h1>
                </div>
                <hr style={{marginTop: "15px"}}></hr>
                <div className="modules">
                    <ul>
                        <li>
                            <button className="openModal" >
                                <div className="option">
                                    <i class="fas fa-cogs fa-3x"></i>
                                    <div className="module-desc">
                                        <h1>Configuration</h1>
                                        <p>Configure and manage available settings for this server</p>
                                    </div>
                                </div>
                            </button>
                        </li>
                        <li>
                            <div className="option">
                                <i class="fas fa-database fa-3x"></i>
                                <div className="module-desc">
                                    <h1>Logging</h1>
                                    <p>Setup different logging options for keeping track of every happening.</p>
                                </div>
                            </div>
                        </li>
                        <li>
                            <div className="option">
                                <i class="fas fa-shield-virus fa-3x"></i>
                                <div className="module-desc">
                                    <h1>Automod</h1>
                                    <p>Enable and manage a variety of automated moderation modules.</p>
                                </div>
                            </div>
                        </li>
                        <li>
                            <div className="option">
                                <i class="fas fa-exclamation-triangle fa-3x"></i>
                                <div className="module-desc">
                                    <h1>Punishments</h1>
                                    <p>Configure punishments when a user reaches a specific amount of warns.</p>
                                </div>
                            </div>
                        </li>
                        <li>
                            <div className="option">
                                <i class="fas fa-tags fa-3x"></i>
                                <div className="module-desc">
                                    <h1>Tags</h1>
                                    <p>Create and delete custom tags/commands for your server.</p>
                                </div>
                            </div>
                        </li>
                    </ul>
                </div>
                <div className="modals">
                    <div id="modal" className="modal">
                        <div className="modal-content">
                            <span className="close">&times;</span>
                            <h1>Server Configurations</h1>
                            <hr style={{marginTop: "15px", marginBottom: "15px"}}></hr>
                            <ConfigModal config={config} roles={roles} channels={channels}/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}