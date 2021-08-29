const router = require('express').Router();
const {fetchBotGuilds, fetchUserGuilds, fetchGuildRoles, fetchGuildChannels} = require('../utils/api');
const {fetchMutualGuilds} = require('../utils/utils');
const User = require('../database/schemas/User');
const GuildConfig = require('../database/schemas/GuildConfig');



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

router.get('/guilds/:guildId/config', async (req, res) => {
    const user = await User.findOne({discordId: req.user.discordId});
    if (user) {
        const userGuilds = await fetchUserGuilds(req.user.discordId);
        if (Object.keys(userGuilds).includes("global")) {
            return res.status(500).send({msg: "Server error"})
        }
        const guildIds = []

        for (const guild of userGuilds) {
            guildIds.push(guild.id)
        }

        const { guildId } = req.params;
        if (guildIds.includes(guildId)) {
            const t = await GuildConfig.findOne();
            console.log(GuildConfig);
            const config = await GuildConfig.findOne({ id: `${guildId}` });
            console.log(config)
            return config ? res.send(config) : res.status(404).send({msg: "Not Found"})
        } else {
            return res.status(401).send({msg: "Unauthorized"})
        }
    } else {
        return res.status(401).send({msg: "Unauthorized"})
    }
})

router.get('/guilds/:guildId/roles', async (req, res) => {
    const { guildId } = req.params;
    try {
     const roles = await fetchGuildRoles(guildId);
     const real = roles.filter(r => r.name !== "@everyone");
     res.send(real)
    } catch (err) {
        console.log(err);
        res.status(500).send({msg: "Internal Server Error | 1"});
    }
 });

router.get('/guilds/:guildId/channels', async (req, res) => {
    const { guildId } = req.params;
    try {
     const channels = await fetchGuildChannels(guildId);
     const real = channels.filter(c => c.type === 0);
     res.send(real)
    } catch (err) {
        res.status(500).send({msg: `Internal Server Error | ${err}`});
    }
});


module.exports = router;