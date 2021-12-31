/* https://github.com/vinnyoodles/reddit-heatmap */

const CELL_SIZE = 14;
const NUMBER_OF_COLORS = 6;
const COUNT_THRESHOLD = 50 /* TODO: this could be an option in UI */

/* Given a CSV file in text form, return a JS object
 * with a start date, end date, a table of dates-count mapping.
 * and max number of counts per date.
 */
function formatCSVData(allText) {
    let allTextLines = allText.split(/\n/);

    let dateTable = {};
    let maxCount = 0;
    let oldestDate = allTextLines[1].split(',')[0];

    // Note, it's (-2) here because the output .csv file has an empty line
    let newestDate = allTextLines[allTextLines.length - 2].split(',')[0];

    // For each date in the CSV file
    for (let i = 1; i < allTextLines.length; i++) {
        let linedata = allTextLines[i].split(',');

        let date = linedata[0];
        let count = parseInt(linedata[1]);

        // Add to return object
        if (dateTable[date]) {
            console.log("that shouldn't happen");
        } else {
            dateTable[date] = { count: count }
        }

        // Update max-count and cap it on threshold
        if (maxCount < count && count < COUNT_THRESHOLD) {
            maxCount = count;
        }
    }

    return {
        startDate: oldestDate,
        endDate: newestDate,
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
    var dx = 18;
    var gridClass = 'js-date-grid day';
    var formatColor = d3.scaleQuantize()
        .domain([0, data.maxCount])
        .range(d3.range(NUMBER_OF_COLORS).map((d) => `color${d}`));

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
        .attr('transform', `translate(-8,${CELL_SIZE * 3.5})rotate(-90)`)
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
        .attr('rx', 4)
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
        .attr('rx', 4)
        .attr('class', (d) => `day color${d - 1}`);

}