import Image from 'next/image';
import _Icon from '../../public/icon.png';



export function Icon() {
    return (
        <Image src={_Icon} alt="icon" width="100px" height="100px"/>
    )
}