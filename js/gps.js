(function ($, L, prettySize) {
	var map, heat,
		heatOptions = {
			tileOpacity: 1,
			heatOpacity: 1,
			radius: 8,
			blur: 5
		};

	function status(message) {
		$('#currentStatus').text(message);
	}

	// Start at the beginning
	var dropzone;
	stageOne();

	function stageOne() {

		// Initialize the map
		map = L.map('map').setView([0, 0], 2);
		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: 'location-history-visualizer is open source and available <a href="https://github.com/FSXAC/location-history-visualizer">on GitHub</a>. Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors.',
			maxZoom: 18,
			minZoom: 2
		}).addTo(map);

		// Initialize the dropzone
		dropzone = new Dropzone(document.body, {
			url: '/',
			previewsContainer: document.createElement('div'), // >> /dev/null
			clickable: false,
			accept: function (file, done) {
				stageTwo(file);
				dropzone.disable(); // Your job is done, buddy
			}
		});

		// For mobile browsers, allow direct file selection as well
		$('#file').change(function () {
			stageTwo(this.files[0]);
			dropzone.disable();
		});
	}

	function stageTwo(file) {
		heat = L.heatLayer([], heatOptions).addTo(map);

		// First, change tabs
		$('body').addClass('working');
		$('#intro').addClass('hidden');
		$('#working').removeClass('hidden');

		var fileSize = prettySize(file.size);
		status('Preparing to import file ( ' + fileSize + ' )...');

		// Now start working!
		parseCSVFile(file);
	}

	function stageThree(numberProcessed) {
		var $done = $('#done');

		// Change tabs :D
		$('body').removeClass('working');
		$('#working').addClass('hidden');
		$done.removeClass('hidden');

		// Update count
		$('#numberProcessed').text(numberProcessed.toLocaleString());

		$('#launch').click(function () {
			$(this).text('Launching... ');
			$('body').addClass('map-active');
			$done.fadeOut();
			activateControls();
		});

		function activateControls() {
			var $tileLayer = $('.leaflet-tile-pane'),
				$heatmapLayer = $('.leaflet-heatmap-layer'),
				originalHeatOptions = $.extend({}, heatOptions); // for reset

			// Update values of the dom elements
			function updateInputs() {
				var option;
				for (option in heatOptions) {
					if (heatOptions.hasOwnProperty(option)) {
						document.getElementById(option).value = heatOptions[option];
					}
				}
			}

			updateInputs();

			$('.control').change(function () {
				switch (this.id) {
					case 'tileOpacity':
						$tileLayer.css('opacity', this.value);
						break;
					case 'heatOpacity':
						$heatmapLayer.css('opacity', this.value);
						break;
					default:
						heatOptions[this.id] = Number(this.value);
						heat.setOptions(heatOptions);
						break;
				}
			});

			$('#reset').click(function () {
				$.extend(heatOptions, originalHeatOptions);
				updateInputs();
				heat.setOptions(heatOptions);
				// Reset opacity too
				$heatmapLayer.css('opacity', originalHeatOptions.heatOpacity);
				$tileLayer.css('opacity', originalHeatOptions.tileOpacity);
			});
		}
	}

	$.ajax({
		type: "GET",
		url: "gps.csv",
		success: function (data) {
			// Basically the same as what's inside stage two
			dropzone.disable();
			heat = L.heatLayer([], heatOptions).addTo(map);

			// First, change tabs
			$('body').addClass('working');
			$('#intro').addClass('hidden');
			$('#working').removeClass('hidden');

			var fileSize = prettySize(file.size);
			status('Preparing to import file ( ' + fileSize + ' )...');


			var latlngs = getLocationDataFromCSV(data);
			heat._latlngs = latlngs;
			heat.redraw();
			stageThree(latlngs.length);
		}
	});

	function parseCSVFile(file) {
		var fileSize = prettySize(file.size);
		var reader = new FileReader();
		reader.onprogress = function (e) {
			var percentLoaded = Math.round((e.loaded / e.total) * 100);
			status(percentLoaded + '% of ' + fileSize + ' loaded...');
		};

		reader.onload = function (e) {
			var latlngs;
			status('Generating map...');
			latlngs = getLocationDataFromCSV(e.target.result);
			heat._latlngs = latlngs;
			heat.redraw();
			stageThree(latlngs.length);
		}
		reader.onerror = function () {
			status('Something went wrong reading your JSON file. Ensure you\'re uploading a "direct-from-Google" JSON file and try again, or create an issue on GitHub if the problem persists. ( error: ' + reader.error + ' )');
		}
		reader.readAsText(file);
	}

	function getLocationDataFromCSV(data) {
		locations = [];
		var lines = data.split(/\n/);
		for (var i = 1; i < lines.length; i++) {
			var entry = lines[i].split(',');
			if (entry.length >= 2) {
				var newloc = [Number(entry[1]), Number(entry[0])];
				locations.push(newloc);
			}
		}

		return locations;
	}

}(jQuery, L, prettySize));
