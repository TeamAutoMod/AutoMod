import styles from "../styles/nav.module.css";

import Logo from "../components/logo";



export default function Navbar() {
    return (
        <div className={styles.nav} >
            <ul>
                {/* <li>
                    <a href={
                        "/"
                    }>
                        <Logo />
                    </a>
                </li> */}
                <li>
                    <a href={
                        "/invite"
                    }>Add to server</a>
                </li>
                <li>
                    <a href={
                        "/support"
                    }>Support</a>
                </li>
                <li>
                    <a href={
                        "https://github.com/TeamAutoMod/AutoMod"
                    }>GitHub</a>
                </li>
                <li>
                    <a href={
                        "/servers"
                    }>Dashboard</a>
                </li>
            </ul>
        </div>
    )
}