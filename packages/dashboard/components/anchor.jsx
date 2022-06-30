import styles from '../styles/anchor.module.css';



export default function Anchor(props) {
    return (
        <a className={styles.anchor} href={props.url} rel="noreferrer" target="_blank">
            {props.children}
        </a>
    )
}