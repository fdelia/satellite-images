var fs = require('fs');
var express = require('express');
var app = express();
var bodyParser = require('body-parser')

app.use(bodyParser.json()); // to support JSON-encoded bodies
app.use(bodyParser.urlencoded({ // to support URL-encoded bodies
	extended: true
}));

app.use(express.static(__dirname + '/app'));
app.listen(process.env.PORT || 8080)

app.use(function(err, req, res, next) {
	//do logging and user-friendly error message display
	res.send(500);
})

app.get('/load/POI', (req, res, next) => {
	if (!req.query.filename) next('loadPOI: not enough parameters')

	var path = getPOIfilePath(req.query.filename)

	fs.access(path, fs.F_OK, (err) => {
		if (!err) {
			// poi-file found
			fs.readFile(path, 'utf-8'	, (err, data) => {
				if (err) throw err;

				var POIs = data
				res.json(POIs)
			})
		} else {
			// no poi-file yet
			console.log('loadPOI: no POI file found')
			res.json([])
		}
	})

})

app.post('/save/POI', (req, res, next) => {
	// console.log(req.body)
	if (!req.body.filename || !req.body.POIs) next('savePOI: not enough parameters')
	else {
		if (typeof(req.body.POIs) != 'string') next('savePOI: POIs have wrong type')

		console.log(req.body.POIs)
		console.log(typeof(req.body.POIs))

		// this is a security risk, however it's ok here
		fs.writeFile(getPOIfilePath(req.body.filename), req.body.POIs, (err) => {
			if (err) {
				console.log('error saving POI-file for ' + req.body.filename)
				console.log(err)
			} else {
				res.send('ok')
			}
		})


		// load POI
		// add the new ones
		// unique
		// save
		// fs.access(path, fs.F_OK, (err) => {
		// 	if (!err) {
		// 		// poi-file found
		// 		fs.readFile(path, (err, data) => {
		// 			if (err) throw err;

		// 			var POIs = getPOIfromFileData(data)


		// 		})
		// 	} else {



		// 	}
		// })



	}
})


app.post('/api/', function(req, res) {
	console.log(req)

});

function getPOIfilePath(filename) {
	return __dirname + '/app/images_input/' + filename + '_POI.txt'
}


// function loadPOI (filename) {
// 	// load file
// 	// split lines, make arrays and objects
// 	var POIs = []


// 	return POIs
// }

// function saveNewPOI(filename, POIs) {
// load POI
// add the new ones
// unique
// save
// }