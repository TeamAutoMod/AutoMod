import { Anchor } from '../components/Anchor';
import styles from '../../styles/Login.module.css';


export default function Login() {
    return (
        <Anchor url="http://localhost:3001/api/auth/discord">
            <div className={styles.login}>
                Login
            </div>
        </Anchor>
    )
};