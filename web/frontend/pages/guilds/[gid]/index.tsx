import { useRouter } from "next/router";
import styles from '../../../styles/Guild.module.css';
import React from 'react';
import { fetchUserDeatils, fetchGuildConfig } from '../../../utils/Api';
import { Config } from '../../types/Config';
import { Plugin } from '../../components/Plugin';



export default function Guild() {
    const router = useRouter();
    const { gid } = router.query;

    const [user, setUser] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [config, setConfig] = React.useState<Config>();

    React.useEffect(() => {
        if(!router.isReady) return;
        fetchUserDeatils()
            .then(({data}) => {
                setUser(data);
                return fetchGuildConfig(gid)
            })
            .then(({data}) => {
                setConfig(data);
                setLoading(false); 
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
                <h1>Plugins - {config?.guild_name}</h1>
            </div>
            <div className={styles.plugins}>
                <ul>
                    <li>
                        <Plugin 
                            h1={"Automoderator"} 
                            p={"Configure automatic moderation, so your mods can just sit back and relax."} 
                            icon={
                                <svg 
                                    xmlns="http://www.w3.org/2000/svg" 
                                    viewBox="0 0 36 36"
                                    width="48px"
                                    height="48px"
                                >
                                    <path fill="#CCD6DD" d="M33 3c-7-3-15-3-15-3S10 0 3 3C0 18 3 31 18 36c15-5 18-18 15-33z"/>
                                    <path fill="#55ACEE" d="M18 33.884C6.412 29.729 1.961 19.831 4.76 4.444 11.063 2.029 17.928 2 18 2c.071 0 6.958.04 13.24 2.444 2.799 15.387-1.652 25.285-13.24 29.44z"/>
                                    <path fill="#269" d="M31.24 4.444C24.958 2.04 18.071 2 18 2v31.884c11.588-4.155 16.039-14.053 13.24-29.44z"/>
                                </svg>
                            }
                            gid={gid}
                            path={"automod"}
                        />
                    </li>
                    <li>
                        <Plugin 
                            h1={"Logging"} 
                            p={"Set up log channels for various events, to keep track of what's happening in your server."} 
                            icon={
                                <svg 
                                    xmlns="http://www.w3.org/2000/svg" 
                                    viewBox="0 0 36 36"
                                    width="48px"
                                    height="48px"
                                >
                                    <path fill="#553788" d="M15 31c0 2.209-.791 4-3 4H5c-4 0-4-14 0-14h7c2.209 0 3 1.791 3 4v6z"/>
                                    <path fill="#9266CC" d="M34 33h-1V23h1c.553 0 1-.447 1-1s-.447-1-1-1H10c-4 0-4 14 0 14h24c.553 0 1-.447 1-1s-.447-1-1-1z"/>
                                    <path fill="#CCD6DD" d="M34.172 33H11c-2 0-2-10 0-10h23.172c1.104 0 1.104 10 0 10z"/>
                                    <path fill="#99AAB5" d="M11.5 25h23.35c-.135-1.175-.36-2-.678-2H11c-1.651 0-1.938 6.808-.863 9.188C9.745 29.229 10.199 25 11.5 25z"/>
                                    <path fill="#269" d="M12 8c0 2.209-1.791 4-4 4H4C0 12 0 1 4 1h4c2.209 0 4 1.791 4 4v3z"/>
                                    <path fill="#55ACEE" d="M31 10h-1V3h1c.553 0 1-.447 1-1s-.447-1-1-1H7C3 1 3 12 7 12h24c.553 0 1-.447 1-1s-.447-1-1-1z"/>
                                    <path fill="#CCD6DD" d="M31.172 10H8c-2 0-2-7 0-7h23.172c1.104 0 1.104 7 0 7z"/>
                                    <path fill="#99AAB5" d="M8 5h23.925c-.114-1.125-.364-2-.753-2H8C6.807 3 6.331 5.489 6.562 7.5 6.718 6.142 7.193 5 8 5z"/>
                                    <path fill="#F4900C" d="M20 17c0 2.209-1.791 4-4 4H6c-4 0-4-9 0-9h10c2.209 0 4 1.791 4 4v1z"/>
                                    <path fill="#FFAC33" d="M35 19h-1v-5h1c.553 0 1-.447 1-1s-.447-1-1-1H15c-4 0-4 9 0 9h20c.553 0 1-.447 1-1s-.447-1-1-1z"/>
                                    <path fill="#CCD6DD" d="M35.172 19H16c-2 0-2-5 0-5h19.172c1.104 0 1.104 5 0 5z"/>
                                    <path fill="#99AAB5" d="M16 16h19.984c-.065-1.062-.334-2-.812-2H16c-1.274 0-1.733 2.027-1.383 3.5.198-.839.657-1.5 1.383-1.5z"/>
                                </svg>
                            } 
                            gid={gid}
                            path={"automod"}
                        />
                    </li>
                    <li>
                        <Plugin 
                            h1={"Configuration"} 
                            p={"Configure general things, like the servers prefix and certain join modes."} 
                            icon={
                                <svg 
                                    xmlns="http://www.w3.org/2000/svg" 
                                    viewBox="0 0 36 36"
                                    width="48px"
                                    height="48px"
                                >
                                    <path fill="#8899A6" d="M27.989 19.977c-.622 0-1.225.078-1.806.213L15.811 9.818c.134-.581.212-1.184.212-1.806C16.023 3.587 12.436 0 8.012 0 7.11 0 5.91.916 6.909 1.915l2.997 2.997s.999 1.998-.999 3.995-3.996.998-3.996.998L1.915 6.909C.916 5.91 0 7.105 0 8.012c0 4.425 3.587 8.012 8.012 8.012.622 0 1.225-.078 1.806-.212l10.371 10.371c-.135.581-.213 1.184-.213 1.806 0 4.425 3.588 8.011 8.012 8.011.901 0 2.101-.916 1.102-1.915l-2.997-2.997s-.999-1.998.999-3.995 3.995-.999 3.995-.999l2.997 2.997c1 .999 1.916-.196 1.916-1.102 0-4.425-3.587-8.012-8.011-8.012z"/>
                                </svg>
                            } 
                            gid={gid}
                            path={"automod"}
                        />
                    </li>
                    <li>
                        <Plugin 
                            h1={"Infractions"} 
                            p={"Check up on recent moderation actions taken in your server, edit or even delete them."} 
                            icon={
                                <svg 
                                    xmlns="http://www.w3.org/2000/svg" 
                                    viewBox="0 0 36 36"
                                    width="48px"
                                    height="48px"
                                >
                                    <path fill="#FFCC4D" d="M2.653 35C.811 35-.001 33.662.847 32.027L16.456 1.972c.849-1.635 2.238-1.635 3.087 0l15.609 30.056c.85 1.634.037 2.972-1.805 2.972H2.653z"/>
                                    <path fill="#231F20" d="M15.583 28.953c0-1.333 1.085-2.418 2.419-2.418 1.333 0 2.418 1.085 2.418 2.418 0 1.334-1.086 2.419-2.418 2.419-1.334 0-2.419-1.085-2.419-2.419zm.186-18.293c0-1.302.961-2.108 2.232-2.108 1.241 0 2.233.837 2.233 2.108v11.938c0 1.271-.992 2.108-2.233 2.108-1.271 0-2.232-.807-2.232-2.108V10.66z"/>
                                </svg>
                            }
                            gid={gid}
                            path={"automod"} 
                        />
                    </li>
                    <li>
                        <Plugin 
                            h1={"Filters"} 
                            p={"Create customisable filters to keep your chat clean from bad words and phrases at all times."} 
                            icon={
                                <svg 
                                    xmlns="http://www.w3.org/2000/svg" 
                                    viewBox="0 0 36 36"
                                    width="48px"
                                    height="48px"
                                >
                                    <path fill="#9AAAB4" d="M31.5 4l-1.784 4.542L27.932 4h-4.147l-1.926 4.903L19.932 4h-3.863l-1.926 4.903L12.216 4H8.068L6.284 8.542 4.5 4H2.133l3.735 28.013h24.263L33.867 4H31.5zm-5.642 1.678l2.459 6.425-2.601 6.621-2.457-6.254 2.599-6.792zM18 6.049l2.457 6.42L18 18.723l-2.457-6.254L18 6.049zm-7.858-.371l2.599 6.792-2.457 6.254-2.601-6.621 2.459-6.425zM5.958 16.611l.326-.853 2.549 6.66-1.573 4.004-1.302-9.811zM8.068 32l2.216-5.79L12.5 32H8.068zm3.668-9.582l2.407-6.288 2.406 6.288-2.406 6.126-2.407-6.126zM15.784 32L18 26.21 20.216 32h-4.432zm3.667-9.582l2.406-6.288 2.406 6.288-2.406 6.126-2.406-6.126zM23.5 32l2.216-5.79L27.932 32H23.5zm5.392-5.192l-1.725-4.39 2.549-6.659.411 1.074-1.235 9.975z"/>
                                    <path fill="#67757F" d="M32 34c0-1.104-.896-2-2-2H6c-1.104 0-2 .896-2 2s.896 2 2 2h24c1.104 0 2-.896 2-2zm4-32c0-1.105-.896-2-2-2H2C.896 0 0 .896 0 2c0 1.105.896 2 2 2h32c1.104 0 2-.895 2-2z"/>
                                </svg>
                            }
                            gid={gid}
                            path={"automod"} 
                        />
                    </li>
                    <li>
                        <Plugin 
                            h1={"Tags"} 
                            p={"Tired of always repeating the same things? Then create custom tags to automate your replying proccess."} 
                            icon={
                                <svg 
                                    xmlns="http://www.w3.org/2000/svg" 
                                    viewBox="0 0 36 36"
                                    width="48px"
                                    height="48px"
                                >
                                    <path fill="#CCD6DD" d="M31 32c0 2.209-1.791 4-4 4H5c-2.209 0-4-1.791-4-4V4c0-2.209 1.791-4 4-4h22c2.209 0 4 1.791 4 4v28z"/>
                                    <path fill="#99AAB5" d="M27 24c0 .553-.447 1-1 1H6c-.552 0-1-.447-1-1 0-.553.448-1 1-1h20c.553 0 1 .447 1 1zm-16 4c0 .553-.448 1-1 1H6c-.552 0-1-.447-1-1 0-.553.448-1 1-1h4c.552 0 1 .447 1 1zM27 8c0 .552-.447 1-1 1H6c-.552 0-1-.448-1-1s.448-1 1-1h20c.553 0 1 .448 1 1zm0 4c0 .553-.447 1-1 1H6c-.552 0-1-.447-1-1 0-.553.448-1 1-1h20c.553 0 1 .447 1 1zm0 4c0 .553-.447 1-1 1H6c-.552 0-1-.447-1-1 0-.553.448-1 1-1h20c.553 0 1 .447 1 1zm0 4c0 .553-.447 1-1 1H6c-.552 0-1-.447-1-1 0-.553.448-1 1-1h20c.553 0 1 .447 1 1z"/>
                                    <path fill="#66757F" d="M31 6.272c-.827-.535-1.837-.579-2.521-.023l-.792.646-1.484 1.211-.1.08-2.376 1.938-11.878 9.686c-.437.357-.793 1.219-1.173 2.074-.378.85-.969 2.852-1.443 4.391-.148.25-1.065 1.846-.551 2.453.52.615 2.326.01 2.568-.076 1.626-.174 3.731-.373 4.648-.58.924-.211 1.854-.395 2.291-.752.008-.006.01-.018.017-.023l11.858-9.666.792-.646.144-.118V6.272z"/>
                                    <path fill="#D99E82" d="M18.145 22.526s-1.274-1.881-2.117-2.553c-.672-.843-2.549-2.116-2.549-2.116-.448-.446-1.191-.48-1.629-.043-.437.438-.793 1.366-1.173 2.291-.472 1.146-1.276 4.154-1.768 5.752-.083.272.517-.45.503-.21-.01.187.027.394.074.581l-.146.159.208.067c.025.082.05.154.068.21l.159-.146c.187.047.394.084.58.074.24-.014-.483.587-.21.503 1.598-.493 4.607-1.296 5.752-1.768.924-.381 1.854-.736 2.291-1.174.439-.435.406-1.178-.043-1.627z"/>
                                    <path fill="#EA596E" d="M25.312 4.351c-.876.875-.876 2.293 0 3.168l3.167 3.168c.876.874 2.294.874 3.168 0l3.169-3.168c.874-.875.874-2.293 0-3.168l-3.169-3.168c-.874-.875-2.292-.875-3.168 0l-3.167 3.168z"/><path fill="#FFCC4D" d="M11.849 17.815l3.17 3.17 3.165 3.166 11.881-11.879-6.337-6.336-11.879 11.879z"/><path fill="#292F33" d="M11.298 26.742s-2.06 1.133-2.616.576c-.557-.558.581-2.611.581-2.611s1.951.036 2.035 2.035z"/>
                                    <path fill="#CCD6DD" d="M23.728 5.935l3.96-3.96 6.336 6.337-3.96 3.96z"/>
                                    <path fill="#99AAB5" d="M26.103 3.558l.792-.792 6.336 6.335-.792.792zM24.52 5.142l.791-.791 6.336 6.335-.792.792z"/>
                                </svg>
                            }
                            gid={gid}
                            path={"automod"} 
                        />
                    </li>
                </ul>
            </div>
        </div>
    )
}