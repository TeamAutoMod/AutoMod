import styles from "../styles/Anchor.module.css";



export default function Anchor(props: {url: string, children: React.ReactNode, target: string}) {
    return (
        <a className={styles.anchor} href={props.url} rel="noreferrer" target={props.target}>
            {props.children}
        </a>
    )
}