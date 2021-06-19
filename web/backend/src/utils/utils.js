const CryptoJS = require('crypto-js');



function getMutualGuilds(userGuilds, botGuilds) {
    const validGuilds = userGuilds.filter((guild) => (guild.permissions & 0x20) === 0x20);

    const included = [];
    const excluded = validGuilds.filter((guild) => {
        const foundGuild = botGuilds.find((g) => g.id === guild.id);
        if (!foundGuild) return guild;
        included.push(foundGuild)
    });
    return {excluded, included}
}

function encrypt(token) {
    return CryptoJS.AES.encrypt(token, process.env.ENCRYPT_PASS_DEV);
};

function decrypt(token) {
    return CryptoJS.AES.decrypt(token, process.env.ENCRYPT_PASS_DEV);
};

module.exports = {getMutualGuilds, encrypt, decrypt}