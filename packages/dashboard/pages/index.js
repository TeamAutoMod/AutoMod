import styles from '../styles/home.module.css'

import Navbar from "../components/nav";



export default function Home() {
  return (
    <>
        <Navbar />
        <div className={styles.container}>
          <div className={styles.wrapper}>
            <div className={styles.text}>
              <h1>
                AutoMod
              </h1>
              <p>
                Advanced Discord moderation & utility bot
              </p>
              <ul>
                <li>
                  <a href="/invite">
                    Add to server
                  </a>
                </li>
                <li>
                  <a href="/support">
                    Join support
                  </a>
                </li>
                <li>
                  <a href="/servers">
                    Manage server
                  </a>
                </li>
              </ul>
            </div>

            <div className={styles.features}>
              <ul>
                <li>
                  <div className={styles.f}>
                    <h1>
                      Automod
                    </h1>
                    <p>
                      Keeps your server clean even when youre sleeping
                    </p>
                  </div>
                  <div className={styles.f}>
                    <h1>
                      Automod
                    </h1>
                    <p>
                      Keeps your server clean even when youre sleeping
                    </p>
                  </div>
                  <div className={styles.f}>
                    <h1>
                      Automod
                    </h1>
                    <p>
                      Keeps your server clean even when youre sleeping
                    </p>
                  </div>
                  <div className={styles.f}>
                    <h1>
                      Automod
                    </h1>
                    <p>
                      Keeps your server clean even when youre sleeping
                    </p>
                  </div>
                  <div className={styles.f}>
                    <h1>
                      Automod
                    </h1>
                    <p>
                      Keeps your server clean even when youre sleeping
                    </p>
                  </div>
                  <div className={styles.f}>
                    <h1>
                      Automod
                    </h1>
                    <p>
                      Keeps your server clean even when youre sleeping
                    </p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
    </>
  )
}
