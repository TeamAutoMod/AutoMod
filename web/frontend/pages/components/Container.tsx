import styles from '../../styles/Container.module.css'



export function Container(props: {children: any}) {
    return (
        <div className={styles.container}>
            {props.children}
        </div>
    )
}