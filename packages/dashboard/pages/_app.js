import "../styles/globals.css";

import Head from "next/head";



function MyApp({ Component, pageProps }) {
  return (
    <>
      <Head>
        <script src="https://kit.fontawesome.com/75daf56dea.js" crossorigin="anonymous"></script>
      </Head>
      <Component {...pageProps} />
    </>
  )
}

export default MyApp
