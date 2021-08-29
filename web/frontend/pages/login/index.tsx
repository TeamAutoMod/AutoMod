import { Anchor } from '../components/Anchor';
import styles from '../../styles/Login.module.css';
import { Wave } from '../components/Wave';



export default function Login() {
    return (
        <div>
            <Anchor url="http://localhost:3001/api/auth/discord">
                <div className={styles.login}>
                    Login with Discord
                </div>
            </Anchor>
            <Wave />
        </div>
    )
};