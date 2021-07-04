/* https://github.com/vinnyoodles/reddit-heatmap */

const CELL_SIZE = 14;
const NUMBER_OF_COLORS = 6;

$.ajax({
    type: "GET",
    url: "heatmap.csv",
    success: function (data) {
        var fdata = formatCSVData(data);
        // console.log(fdata);
        // TODO:
        createHeatMap(fdata, '2017', '2022');
    }
});

function formatCSVData(allText) {
    var allTextLines = allText.split(/\n/);
    // var headers = allTextLines[0].split(',');
    // var lines = [];

    var dateTable = {};
    var maxCount = 0;
    var oldestDate = allTextLines[1][0];

    // var format = d3.timeFormat('%Y-%m-%d');

    for (var i = 1; i < allTextLines.length; i++) {
        var linedata = allTextLines[i].split(',');
        
        var date = linedata[0];
        var count = parseInt(linedata[1]);

        if (dateTable[date]) {
            console.log("that shouldn't happen");
        } else {
            dateTable[date] = { count: count }
        }

        if (maxCount < count && count < 50) {
            maxCount = count;
        }
    }

    return {
        startDate: oldestDate,
        dates: dateTable,
        maxCount
    };
}


function formatData(data) {
    var oldestDate = new Date();
    var maxCount = 0;
    var dateTable = {};

    for (var key in data) {
        var value = data[key];
        if (!value || !value.length || !key) continue;

        var lastDate = new Date(value[value.length - 1].created * 1000);
        oldestDate = Math.min(oldestDate, lastDate);
        value.forEach((entity) => {
            var format = d3.timeFormat('%Y-%m-%d');
            // Created is a date timestamp in seconds.
            var date = format(new Date(entity.created * 1000));

            if (dateTable[date]) {
                var typeCount = dateTable[date][key];
                dateTable[date][key] = typeCount ? typeCount + 1 : 1;
                dateTable[date].count++;
            } else {
                dateTable[date] = { count: 1 };
                dateTable[date][key] = 1;
            }

            maxCount = Math.max(maxCount, dateTable[date].count);
        });
    }

    return {
        startDate: new Date(oldestDate),
        dates: dateTable,
        maxCount
    };
}

/**
 * Render the heatmap and any other svg elements
 * @param  {Object} data
 * @param  {Date} startYear
 * @param  {Date} endYear
 */
function createHeatMap(data, startYear, endYear) {
    var width = 900;
    var height = 110;
    var dx = 35;
    var gridClass = 'js-date-grid day';
    var formatColor = d3.scaleQuantize().domain([0, data.maxCount]).range(d3.range(NUMBER_OF_COLORS).map((d) => `color${d}`));

    var heatmapSvg = d3.select('.js-heatmap').selectAll('svg.heatmap')
        .enter()
        .append('svg')
        .data(d3.range(startYear, endYear))
        .enter()
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'color')

    // Add a grid for each day between the date range.
    var dates = Object.keys(data.dates);
    var rect = heatmapSvg.append('g')
        .attr('transform', `translate(${dx},0)`);

    // Add year label.
    rect.append('text')
        .attr('transform', `translate(-9,${CELL_SIZE * 3.5})rotate(-90)`)
        .style('text-anchor', 'middle')
        .text((d) => d);

    rect.selectAll('.day')
        // The heatmap will contain all the days in that year.
        .data((d) => d3.timeDays(new Date(d, 0, 1), new Date(d + 1, 0, 1)))
        .enter()
        .append('rect')
        .attr('class', gridClass)
        .attr('width', CELL_SIZE)
        .attr('height', CELL_SIZE)
        .attr('x', (d) => d3.timeFormat('%U')(d) * CELL_SIZE)
        .attr('y', (d) => d.getDay() * CELL_SIZE)
        .attr('data-toggle', 'tooltip')
        .datum(d3.timeFormat('%Y-%m-%d'))
        // Add the grid data as a title attribute to render as a tooltip.
        .attr('title', (d) => {
            var countData = data.dates[d];
            var date = d3.timeFormat('%b %d, %Y')(new Date(d));
            if (!countData || !countData.count) return `No photos on ${date}`;
            else if (countData.count === 1) return `1 photo on ${date}`;
            else return `${countData.count} photos on ${date}`;
        })
        .attr('date', (d) => d)
        // Add bootstrap's tooltip event listener.
        .call(() => $('[data-toggle="tooltip"]').tooltip({
            container: 'body',
            placement: 'top',
            position: { my: 'top' }
        }))
        // Add the colors to the grids.
        .filter((d) => dates.indexOf(d) > -1)
        .attr('class', (d) => `${gridClass} ${formatColor(data.dates[d].count)}`)

    // Render x axis to show months
    d3.select('.js-months').selectAll('svg.months')
        .enter()
        .append('svg')
        .data([1])
        .enter()
        .append('svg')
        .attr('width', 800)
        .attr('height', 20)
        .append('g')
        .attr('transform', 'translate(0,10)')
        .selectAll('.month')
        .data(() => d3.range(12))
        .enter()
        .append('text')
        .attr('x', (d) => d * (4.5 * CELL_SIZE) + dx)
        .text((d) => d3.timeFormat('%b')(new Date(0, d + 1, 0)));

    // Render the grid color legend.
    var legendSvg = d3.select('.js-legend').selectAll('svg.legend')
        .enter()
        .append('svg')
        .data([1])
        .enter()
        .append('svg')
        .attr('width', 800)
        .attr('height', 20)
        .append('g')
        .attr('transform', 'translate(644,0)')
        .selectAll('.legend-grid')
        .data(() => d3.range(7))
        .enter()
        .append('rect')
        .attr('width', CELL_SIZE)
        .attr('height', CELL_SIZE)
        .attr('x', (d) => d * CELL_SIZE + dx)
        .attr('class', (d) => `day color${d - 1}`);

}
