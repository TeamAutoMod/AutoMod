import { useRouter } from "next/router";

export default function Guild() {
    const router = useRouter();
    const { gid } = router.query;

    return (
        <h1>
            Dashboard for {gid}
        </h1>
    )
}