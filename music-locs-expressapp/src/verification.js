const { createHash } = require('crypto');



function verifyApiToken(db, token) {
	db.connect(function(err) {
		if (err) throw err;
		db.query("SELECT (uid, expiration_date) FROM api_tokens WHERE token = '?'", [createHash('sha256').update(token).digest('base64')], function (err, result) {
			if (err) throw err;
			//console.log(result);
		});
	});

	if (!result) {
		return 1;
	}
	return 0;
};

module.exports = { verifyApiToken }
