const router = require('express').Router();
const {fetchBotGuilds, fetchUserGuilds} = require('../utils/api');
const {fetchMutualGuilds} = require('../utils/utils');
const User = require('../database/schemas/User');



router.get("/guilds", async (req, res) => {
    const botGuilds = await fetchBotGuilds();
    // if (req.user === undefined) {return res.status(401).send({msg: "Unauthorized"})};
    const user = await User.findOne({discordId: req.user.discordId});
    if (user) {
        const userGuilds = await fetchUserGuilds(req.user.discordId);
        const guilds = fetchMutualGuilds(userGuilds, botGuilds);
        res.send(guilds);
    } else {
        return res.status(401).send({msg: "Unauthorized"})
    }
});

module.exports = router;