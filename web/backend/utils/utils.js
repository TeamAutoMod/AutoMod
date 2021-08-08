const CryptoJS = require('crypto-js');



function fetchMutualGuilds(userGuilds, botGuilds) {
    const valid = userGuilds.filter((g) => (g.permissions & 0x20) == 0x20);
    const included = [];
    const excluded = valid.filter((g) => {
        const foundGuild = botGuilds.find((_g) => _g.id === g.id);
        if (!foundGuild) return g;
        included.push(foundGuild)
    });
    return {excluded, included};
};

function encrypt(token) {
    return CryptoJS.AES.encrypt(token, process.env.ENCRYPT);
};

function decrypt(token) {
    return CryptoJS.AES.decrypt(token, process.env.ENCRYPT);
};


module.exports = {fetchMutualGuilds, encrypt, decrypt}