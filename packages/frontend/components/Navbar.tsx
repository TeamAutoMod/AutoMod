import styles from "../styles/Navbar.module.css";
import Anchor from "./Anchor";



export default function Navbar() {
    return (
        <div className={styles.nav}>
            <ul className={styles.ul}>
                <li className={styles.li}>
                    <Anchor url="/invite" target="_self"><h1>Add to Discord</h1></Anchor>
                </li>
                <li className={styles.li}>
                    <Anchor url="https://discord.gg/S9BEBux" target="_self"><h1>Support</h1></Anchor>
                </li>
                <li className={styles.li}>
                    <Anchor url="https://top.gg/bot/697487580522086431/vote" target="_self"><h1>Vote</h1></Anchor>
                </li>
                <li className={styles.li}>
                    <Anchor url="https://github.com/TeamAutoMod/AutoMod" target="_self"><h1>GitHub</h1></Anchor>
                </li>
            </ul>
        </div>
    )
}