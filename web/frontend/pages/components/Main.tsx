import styles from '../../styles/Main.module.css'



export function Main(props: {top: number, left: number, transform_x: number, transform_y: number, children: any, }) {
    return (
        <main className={styles.main} style={
            {
                top: `${props.top}%`, 
                left: `${props.left}%`, 
                transform: `translate(-${props.transform_x}%, -${props.transform_y}%)`}
            }
        >
            {props.children}
        </main>
    )
}