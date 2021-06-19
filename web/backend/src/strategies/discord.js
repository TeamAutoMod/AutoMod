const passport = require('passport');
const DiscordStrategy = require('passport-discord');
const User = require('../database/schemas/User');
const OAuth2Credentials = require('../database/schemas/OAuth2Credentials');
const { encrypt } = require('../utils/utils');


passport.serializeUser((user, done) => {
    done(null, user.discordId)
})

passport.deserializeUser(async (discordId, done) => {
    try {
        const user = await User.findOne({discordId})
        return user ? done(null, user) : done(null, null)
    } catch(err) {
        console.log(err);
        done(err, null)
    }
})
passport.use(new DiscordStrategy({
    clientID: process.env.CLIENT_ID,
    clientSecret: process.env.CLIENT_SECRET,
    callbackURL: process.env.CALLBACK_URL,
    scope: ["identify", "guilds"]
},  async (accessToken, refreshToken, profile, done) => {
    try {
        const encryptedAccessToken = encrypt(accessToken).toString();
        const encryptedRefreshToken = encrypt(refreshToken).toString();
        const {id, username, discriminator, avatar, guilds} = profile;
        const foundUser = await User.findOneAndUpdate({discordId: id}, {
            discordTag: `${username}#${discriminator}`,
            avatar,
            guilds
        }, {new: true})
        const foundCredentials = await OAuth2Credentials.findOneAndUpdate({ discordId: id }, {
            access_token: encryptedAccessToken,
            refresh_token: encryptedRefreshToken
        })
        if (foundUser) {
            if (!foundCredentials) {
                const newCredentials = await OAuth2Credentials.create({
                    access_token: encryptedAccessToken,
                    refresh_token: encryptedRefreshToken,
                    discordId: id
                });   
            }
            return done(null, foundUser)
        } else {
            const newUser = await User.create({
                discordId: id,
                discordTag: `${username}#${discriminator}`,
                avatar,
                guilds
            })
            const newCredentials = await OAuth2Credentials.create({
                access_token: encryptedAccessToken,
                refresh_token: encryptedRefreshToken,
                discordId: id
            });
            return done(null, newUser)
        }
    } catch(err) {
        console.log(err);
        return done(err, null);
    }
})
)