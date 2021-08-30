import styles from '../../styles/Plugin.module.css';
import { Anchor } from '../components/Anchor';



export function Plugin(props: {h1: string, p: string, icon: any, gid: any, path: string}) {
    const icon = () => {
        return (
            props.icon
        )
    }
    return (
        <Anchor url={`/guilds/${props.gid}/${props.path}`} >
            <div className={styles.plugin}>
                <div className={styles.plugin_icon}>
                    {icon()}
                </div>
                <div className={styles.plugin_text}>
                    <h1>
                        {props.h1}
                    </h1>
                    <p>
                        {props.p}
                    </p>
                </div>
            </div>
        </Anchor>
    )
}