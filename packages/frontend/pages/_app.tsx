import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { ThemeProvider } from "next-themes";
import Head from "next/head";



function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>AutoMod</title>
        <link rel="icon" type="image/x-icon" href="favicon.ico"></link>
        <meta content="Discord moderation & utility bot" name="description" />
        <meta content="280" property="og:image:width" />
        <meta content="280" property="og:image:height" />
        <meta content="Discord moderation & utility bot" property="og:description" />
        <meta content="AutoMod" property="og:title" />
      </Head>

      <ThemeProvider defaultTheme="dark">
        <Component {...pageProps} />
      </ThemeProvider>
    </>
  )
}

export default MyApp
