const mongoose = require('mongoose');



module.exports = mongoose.connect(process.env.DB_PASS, { useNewUrlParser: true, useUnifiedTopology: true });