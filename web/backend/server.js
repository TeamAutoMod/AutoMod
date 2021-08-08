require('dotenv').config();
require('./strategies/discord');

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const session = require('express-session');
const passport = require('passport');

const App = express();
const PORT = process.env.PORT || 3002;
const routes = require("./routes");
const MongoStore = require('connect-mongo');

mongoose.connect(process.env.DB_HOST, {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

App.use(express.json());
App.use(express.urlencoded({extended: false}));

App.use(cors({
    origin: ["http://localhost:3000"],
    credentials: true
}));

App.use(session({
    secret: process.env.COOKIE_SECRET,
    cookie: {
        maxAge: 60000 * 60 * 24
    },
    resave: false,
    saveUninitialized: false,
    store: MongoStore.create({
        mongoUrl: process.env.DB_HOST
    })
}));

App.use(passport.initialize());
App.use(passport.session());

App.use("/api", routes);
App.listen(PORT, () => console.log(`API server running on port ${PORT}`));