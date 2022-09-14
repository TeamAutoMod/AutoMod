import type { NextPage } from 'next'
import Navbar from "../components/Navbar";
import styles from '../styles/Home.module.css'



const Home: NextPage = () => {
  return (
    <div className={styles.container}>
      <Navbar />
    </div>
  )
}

export default Home