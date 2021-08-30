import styles from '../../styles/GuildCard.module.css';
import { Guild } from '../types/Guild';
import { Anchor } from '../components/Anchor';



export function GuildCard(props: {guild: Guild, manage: boolean}) {
    const guild = props.guild;
    return (
        <div className={styles.card}>
            <Anchor url={props.manage === true ? `/guilds/${guild.id}` : "https://discord.com/oauth2/authorize?client_id=697487580522086431&scope=bot&permissions=403041534"}>
                <img className={styles.guild_icon} src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=1024`} />
                <div className={styles.name}>
                    <h1>{guild.name}</h1>
                </div>
            </Anchor>
        </div>
    )
}