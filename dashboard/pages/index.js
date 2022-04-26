import Head from 'next/head'
import Image from 'next/image'
import styles from '../styles/Home.module.css'
import Logo from '../public/icon.png';

export default function Home() {
  return (
    <div className={styles.container}>
        <div className={styles.text}>
            <h1>
                AutoMod
            </h1>

            <div className={styles.desc}>
                <p>
                    AutoMod is a Discord moderation and utility bot, made for both small and large communities.
                </p>
            </div>

            <div className={styles.buttons}>
                <a href="/invite" className={styles.btn}>
                    Add to server
                </a>
            </div>
            
            <ul className={styles.links}>
                <li>
                    <a href="https://discord.gg/S9BEBux " target="_blank">
                        Support
                    </a>
                </li>
                <li>
                    <a href="https://github.com/TeamAutoMod/AutoMod" target="_blank">
                        GitHub
                    </a>
                </li>
                <li>
                    <a href="https://top.gg/bot/697487580522086431/vote" target="_blank">
                        Top.gg
                    </a>
                </li>
                <li>
                    <a href="https://twitter.com/AutoModBot" target="_blank">
                        Twitter
                    </a>
                </li>
            </ul>
        </div>

        <div className={styles.logo}>
            <Image src={Logo} alt="AutoMod Icon" width={300} height={300}/>
        </div>
    </div>
  )
}
