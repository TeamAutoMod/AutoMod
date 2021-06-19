const path = require('path');
require('dotenv').config({path: path.join(__dirname, "/.env")});
require('./strategies/discord');

const express = require('express');
const passport = require('passport');
const mongoose = require('mongoose');
const session = require('express-session');
const cors = require('cors');
const Store = require('connect-mongo');

const app = express();
const routes = require('./routes');


mongoose.connect(`${process.env.MONGO_URL}main`, {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

app.use(cors({
    origin: ["http://localhost:3000"],
    credentials: true
}));

app.use(session({
    secret: process.env.SESSION_SECRET,
    cookie: {
        maxAge: 60000 * 60 * 24
    },
    resave: false,
    saveUninitialized: false,
    store: Store.create({
        mongoUrl: process.env.MONGO_URL
    })
}));

app.use(passport.initialize());
app.use(passport.session());

app.use('/api', routes);






const PORT = process.env.PORT || 3002;
app.listen(PORT, () => console.log(`Server running on port ${ PORT }`));