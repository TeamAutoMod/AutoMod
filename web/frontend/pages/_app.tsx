import React from 'react';
import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { ThemeProvider } from "next-themes";
import Head from "next/head";
import { Navbar } from './components/Navbar';



export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <script src="https://kit.fontawesome.com/f2afea373b.js" crossOrigin="anonymous"></script>
      </Head>
      
      <ThemeProvider defaultTheme="dark">
          <Navbar />
          <Component {...pageProps} />
      </ThemeProvider>
    </>
  )
}