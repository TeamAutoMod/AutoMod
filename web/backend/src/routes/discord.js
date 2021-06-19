const router = require('express').Router();
const { getBotGuilds, getUserGuilds, getGuildChannels, getGuildRoles } = require('../utils/api');
const { getMutualGuilds } = require('../utils/utils');
const User = require('../database/schemas/User');
const GuildConfig = require('../database/schemas/GuildConfig');


router.get("/guilds", async (req, res) => {
    const guilds = await getBotGuilds()
    const user = await User.findOne({discordId: req.user.discordId})
    if (user) {
        const userGuilds = await getUserGuilds(req.user.discordId)
        const mutualGuilds = getMutualGuilds(userGuilds, guilds)
        res.send(mutualGuilds)
    } else {
        return res.status(401).send({msg: "Unauthorized"})
    }
})


router.get("/guilds/:guildId/config", async (req, res) => {
    const user = await User.findOne({discordId: req.user.discordId});
    if (user) {
      const userGuilds = await getUserGuilds(user.discordId);
      if (!Array.isArray(userGuilds)) {
          return res.status(429).send({msg: "Ratelimited"})
      }
      const guildIds = []
      userGuilds.forEach(guild => guildIds.push(guild["id"]));
      const { guildId } = req.params;
      if (guildIds.includes(guildId)) {
        const config = await GuildConfig.findOne({ id: guildId });
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
        const roles = await getGuildRoles(guildId);
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
        const channels = await getGuildChannels(guildId);
        const real = channels.filter(c => c.type === 0);
        res.send(real)
    } catch (err) {
        res.status(500).send({msg: `Internal Server Error | ${err}`});
    }
});


module.exports = router;