const mongoose = require('mongoose');

const OAuth2CredentialsSchema = new mongoose.Schema({
    access_token: {
        type: String,
        required: true
    },
    refresh_token: {
        type: String,
        required: true
    },
    discordId: {
        type: String,
        required: true
    }
});

module.exports = mongoose.model('OAuth2Credentials', OAuth2CredentialsSchema);