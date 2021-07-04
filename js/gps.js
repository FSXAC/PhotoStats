

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
	// stageOne();
	map = L.map('map').setView([0, 0], 2);
		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: 'location-history-visualizer is open source and available <a href="https://github.com/FSXAC/location-history-visualizer">on GitHub</a>. Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors.',
			maxZoom: 18,
			minZoom: 2
		}).addTo(map);
	

	
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
			heat = L.heatLayer([], heatOptions).addTo(map);

			// First, change tabs
			$('body').addClass('working');
			$('#intro').addClass('hidden');
			$('#working').removeClass('hidden');

			var fileSize = prettySize(file.size);
			status('Preparing to import file ( ' + fileSize + ' )...');

			console.log(data);
			var latlngs = getLocationDataFromCSV(data);
			heat._latlngs = latlngs;
			heat.redraw();
			stageThree(latlngs.length);
		}
	});

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