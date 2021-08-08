import Head from 'next/head'
import { Anchor } from './components/Anchor';
import styles from '../styles/Home.module.css'

export default function Home() {
  return (
    <div className={styles.container}>
      <Head>
        <title>AutoMod</title>
      </Head>


      <main className={styles.main}>

        <div className={styles.text}>
          <h1>AutoMod</h1>
          <p>Advanced moderation for your community</p>
        </div>


        <div className={styles.buttons}>
          <ul>
            <li>
              <Anchor url="https://discord.com/oauth2/authorize?client_id=697487580522086431&scope=bot&permissions=403041534">
                <div className={styles.btn}>
                  <i className="fas fa-plus-circle"></i>&nbsp;Invite
                </div>
              </Anchor>
            </li>


            <li>
              <Anchor url="/guilds">
                <div className={styles.btn}>
                  <i className="fas fa-cog"></i>&nbsp;Dashboard
                </div>
              </Anchor>
            </li>

            <li>
              <Anchor url="https://discord.gg/S9BEBux">
                <div className={styles.btn}>
                  <i className="fas fa-question-circle"></i>&nbsp;Support
                </div>
              </Anchor>
            </li>
          </ul>
        </div>


        <div className={styles.features}>
          <ul>
            <li>
              <div className={styles.feature}>
                <i className="fas fa-shield-alt fa-2x"></i>
                <h1>Automoderator</h1>
                <p>Customizable automod features to keep your server clean.</p>
              </div>
            </li>

            <li>
              <div className={styles.feature}>
              <i className="fas fa-tags fa-2x"></i>
                <h1>Custom Tags</h1>
                <p>Create tags to automate replying.</p>
              </div>
            </li>

            <li>
              <div className={styles.feature}>
                <i className="fas fa-gavel fa-2x"></i>
                <h1>Moderation</h1>
                <p>Easy-to-use mod commands with clean log messages.</p>
              </div>
            </li>
          </ul>
        </div>
      </main>
    </div>
  )
}
