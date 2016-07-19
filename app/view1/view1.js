'use strict';

angular.module('myApp.view1', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
	$routeProvider.when('/view1', {
		templateUrl: 'view1/view1.html',
		controller: 'viewImgCtrl',
		controllerAs: 'vm',
		bindToController: true
	});
}])

.controller('viewImgCtrl', ['$timeout', '$interval', '$http', function($timeout, $interval, $http) {
	var vm = this;
	console.log('load controller viewImgCtrl')

	vm.POIs = []
	vm.image = {}
	vm.mouse = {}
	vm.labels = LABELS // see on bottom
	vm.activeLabel = 1

	var img = document.getElementById('theImage') // is actually a canvas not an img
	var ctx = img.getContext("2d")

	vm.addPOI = addPOI
		// vm.activeLabel = activeLabel
	vm.savePOIs = savePOIs
		// vm.loadPOIs = loadPOIs
	vm.mouseMove = mouseMove
	vm.mouseDown = mouseDown
		// vm.mouseUp = mouseUp



	// init
	showImage('zurich.jpeg')

	var saveHdlr = $interval(() => {
		savePOIs(vm.image.filename)
	}, 15 * 1000)


	function showImage(filename) {
		// set image to img-tag for browser to load
		vm.image = {
			filename: filename,
			path: 'images_input/' + filename
		}

		var realImg = new Image()
		realImg.src = vm.image.path
		realImg.onload = function() {
			img.width = realImg.width
			img.height = realImg.height

			// load it here, else the POI-points are painted over
			loadPOIs(filename)
		}


		// show POIs on image
		drawAllPOIs()
		writeMessage('image loaded')
	}

	function drawAllPOIs() {
		for (var i = 0; i < vm.POIs.length; i++) {
			var POI = vm.POIs[i]
				// drawPOI(POI.labelNr, POI.x, POI.y)
			drawPOI(POI[0], POI[1], POI[2])
		}
	}

	function mouseMove(event) {
		vm.mouse.x = event.offsetX ? (event.offsetX) : event.pageX - img.offsetLeft
		vm.mouse.y = event.offsetY ? (event.offsetY) : event.pageY - img.offsetTop
	}

	function mouseDown(event) {
		vm.mouse.x = event.offsetX ? (event.offsetX) : event.pageX - img.offsetLeft
		vm.mouse.y = event.offsetY ? (event.offsetY) : event.pageY - img.offsetTop

		addPOI(vm.activeLabel, vm.mouse.x, vm.mouse.y)
		drawPOI(vm.activeLabel, vm.mouse.x, vm.mouse.y)
	}

	// unused for the moment
	// function mouseUp(event) {
	// vm.mouse.x = event.offsetX ? (event.offsetX) : event.pageX - img.offsetLeft
	// vm.mouse.y = event.offsetY ? (event.offsetY) : event.pageY - img.offsetTop

	// drawPOI(0, vm.mouse.x, vm.mouse.y)
	// }

	// x and y are where the user clicks, so the center of the POI
	function addPOI(labelNr, x, y) {
		// vm.POIs.push({
		// 	labelNr: labelNr,
		// 	x: x,
		// 	y: y
		// })
		vm.POIs.push([labelNr, x, y])
	}

	function drawPOI(labelNr, x, y) {
		// ctx.fillStyle = '#FF0000' // red for the momet
		// ctx.fillStyle = LABELS[labelNr].color
		ctx.fillStyle = LABELS[labelNr].color
		ctx.fillRect(x, y, 5, 5)

		// ctx.strokeStyle = '#FF0000'
		// ctx.beginPath();
		// ctx.arc(x, y, 4, 0, 2 * Math.PI);
		// ctx.stroke();

	}

	function savePOIs(filename) {
		var data = {
			filename: filename,
			POIs: JSON.stringify(vm.POIs)
		}
		$http.post('/save/POI', data, {}).then((res) => {
			// success
			writeMessage(vm.POIs.length + ' POIs saved')
			console.log('POIs saved')
		}, (res) => {
			// error
			writeMessage('error saving POIs: ' + res)
		})
	}

	function loadPOIs(filename) {
		$http.get('/load/POI/?filename=' + filename).then((res) => {
			vm.POIs = JSON.parse(res.data)

			drawAllPOIs()
		}, (res) => {

		})
	}

	// not so optimal but it's ok for now
	function writeMessage(message) {
		vm.message = message

		// $timeout(() => {
		// 	vm.message = ''
		// }, 1500)
	}


	// function canvas_arrow(context, fromx, fromy, tox, toy) {
	// 	var headlen = 10; // length of head in pixels
	// 	var angle = Math.atan2(toy - fromy, tox - fromx);
	// 	context.moveTo(fromx, fromy);
	// 	context.lineTo(tox, toy);
	// 	context.lineTo(tox - headlen * Math.cos(angle - Math.PI / 6), toy - headlen * Math.sin(angle - Math.PI / 6));
	// 	context.moveTo(tox, toy);
	// 	context.lineTo(tox - headlen * Math.cos(angle + Math.PI / 6), toy - headlen * Math.sin(angle + Math.PI / 6));
	// }


}]);

// TODO: put this somewhere globally
// width and length have no effect so far, there is only a quadrat "size"
const LABELS = [{
	// zero label for "nothing"
	color: 'yellow',
	name: 'nothing',
}, {
	color: 'red',
	name: 'house',
}, {
	color: '#33FE4E',
	name: 'tree',
}, {
	color: 'blue',
	name: 'water',
}, {
	color: 'white',
	name: 'street / pathway'
}]