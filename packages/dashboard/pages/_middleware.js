import { NextResponse } from "next/server";


export async function middleware(req, _) {
    const { pathname } = req.nextUrl;
    switch(pathname) {
        case "/invite": {
            return NextResponse.redirect("https://discord.com/oauth2/authorize?client_id=697487580522086431&permissions=1374620609647&scope=bot+applications.commands");
        }

        case "/support": {
            return NextResponse.redirect("https://discord.gg/S9BEBux");
        }
        
        default:
            return NextResponse.next();
    }
}