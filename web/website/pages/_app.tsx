import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { ThemeProvider } from "next-themes";
import Head from "next/head";



export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      {/* <Head>
        <link rel="icon" href="/favicon.ico" />
      </Head> */}

      <ThemeProvider defaultTheme="dark">
        <Component {...pageProps} />
      </ThemeProvider>

    </>
  )
}