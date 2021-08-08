import styles from '../../styles/Navbar.module.css';
import { Anchor } from './Anchor';



export function Navbar() {
    return (
        <div className={styles.navbar} >
            <ul>
                <li>
                    <div className={styles.image}>
                        <img src={"https://cdn.discordapp.com/attachments/870057721028837427/870064292102299678/output-onlinepngtools_31.png"}/>
                    </div>
                </li>
                <li>
                    <Anchor url="/">Home</Anchor>
                </li>
                <li>
                    <Anchor url="/invite">Invite</Anchor>
                </li>
                <li>
                    <Anchor url="https://discord.gg/S9BEBux">Support</Anchor>
                </li>
            </ul>
        </div>
    )
}