require('dotenv').config()

const express = require("express");
const PORT = process.env.PORT || 3001;
const app = express();
const path = require("path");



const stats = {
    guilds: 0,
    users: 0
}


app.use(express.static(__dirname + '/pages'));
app.use(express.json());


app.get("/", (_, res) => {
    res.sendFile(
        path.join(__dirname + "/pages/index.html")
    )
})


app.get("/invite", (_, res) => {
    res.redirect(process.env.BOT_INVITE)
})


app.get("/privacy", (_, res) => {
    res.sendFile(
        path.join(__dirname + "/pages/privacy.html")
    )
})


app.get("/terms", (_, res) => {
    res.sendFile(
        path.join(__dirname + "/pages/tos.html")
    )
})


app.post("/pstats", (req, res) => {
    if (req.body?.token != process.env.BOT_TOKEN) {
        res.status(401).send("Unauthorized");
    } else {
        stats.guilds = req.body?.guilds;
        stats.users = req.body?.users;
        res.send(req.body)
    }
})


app.get("/stats", (req, res) => {
    res.json({
        guilds: stats.guilds,
        users: stats.users
    })
})


app.use((_, res, __) => {
    res.status(404).redirect("/");
})


app.listen(PORT, () => console.log(`Listening on port ${PORT}`))