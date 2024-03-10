import express from 'express';
import bodyParser from 'body-parser';
var request = require('request');
let redis = require('redis');
const mariadb = require('mariadb');

var client_id = process.env.CLIENT_ID;
var redirect_uri = 'http://62.107.184.114/api/spotify/callback';

const app = express();
let redisDB = redis.createClient(6379, "localhost");
const sqldb = mariadb.createPool({
	host: process.env.MYSQL_HOSTNAME, 
	user:'root', 
	password: process.env.MYSQL_ROOT_PASSWORD,
	connectionLimit: 5,
	database: "musiclocs"
});

app.use(bodyParser.json());
app.use(function(req, res, next) {
    if (!req.headers.authorization) {
      return res.status(403).json({ error: 'No credentials sent!' });
    }
    next();
});

app.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello, World!' });
});


let todos = [];

app.get('/api/todos', (req, res) => {
  res.json(todos);
});

app.post('/api/todos', (req, res) => {
  const newTodo = req.body;
  todos.push(newTodo);
  res.status(201).json(newTodo);
});

// Handle Spotify Login
app.get("/api/spotify/login", (req, res) => {
    var state = generateRandomString(32);
    var scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control playlist-read-private user-follow-read user-top-read user-read-recently-played user-library-read';

    redisDB.set(state, JSON.stringify(req.query.client_id), function(err, reply){
        //console.log(reply);

		res.redirect('https://accounts.spotify.com/authorize?' +
			querystring.stringify({
			response_type: 'code',
			client_id: client_id,
			scope: scope,
			redirect_uri: redirect_uri,
			state: state
		}));
	});
});

// Handle Spotify Callback
app.get("/api/spotify/callback", (req, res) => {
	var code = req.query.code || null;
	var state = req.query.state || null;
  
	if (state === null) {
		res.redirect('/#' + querystring.stringify({
			error: 'state_mismatch'
		}));
	} else {
		var authOptions = {
			url: 'https://accounts.spotify.com/api/token',
			form: {
				code: code,
				redirect_uri: redirect_uri,
				grant_type: 'authorization_code'
			},
			headers: {
				'content-type': 'application/x-www-form-urlencoded',
				'Authorization': 'Basic ' + (new Buffer.from(client_id + ':' + client_secret).toString('base64'))
			},
			json: true
		};

		con.connect(function(err) {
			if (err) throw err;
			var sql = "INSERT INTO spotify (name, address) VALUES ('Company Inc', 'Highway 37')";
			con.query(sql, function (err, result) {
			  if (err) throw err;
			});
		});
		
		request.post(authOptions, function(error, response, body) {
			if (!error && response.statusCode === 200) {
				res.json({
					"access_token": body.access_token,
					"token_type": body.token_type
				});
			} else {
				console.log('Error getting OAuth Token: ', error);
				res.redirect('/#' + querystring.stringify({
					error: 'invalid_token'
				}));
			}
		});
	}
});

export default app;
