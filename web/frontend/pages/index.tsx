import Head from 'next/head'
import { Anchor } from './components/Anchor';
import { Wave } from './components/Wave';
import { Main } from './components/Main';
import { Container } from './components/Container';
import styles from '../styles/Home.module.css'

export default function Home() {
  return (
    <Container>
      <Head>
        <script src="https://kit.fontawesome.com/f2afea373b.js" crossOrigin="anonymous"></script>
        <title>AutoMod</title>
      </Head>

      <Main top={50} left={50} transform_x={50} transform_y={50}>
        <div className={styles.text}>
          <h1>AutoMod - Keep your community safe</h1>
          <p>
            Powerful automoderation, combined with out-of-the-box moderation <br/> commands, custom tags and much much more.
          </p>
        </div>

        <div className={styles.buttons}>
          <ul>
            <li>
              <Anchor url="/guilds">
                <div className={styles.btn}>
                  Dashboard
                </div>
              </Anchor>
            </li>

            <li>
              <Anchor url="https://discord.com/oauth2/authorize?client_id=697487580522086431&scope=bot&permissions=403041534">
                <div className={styles.btn2}>
                  Invite
                </div>
              </Anchor>
            </li>
          </ul>
        </div>

      </Main>
      <Wave />
    </Container>
  )
}
