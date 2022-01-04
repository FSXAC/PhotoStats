function drawGraph(data) {

    /* Constants */
    const defaultOpacity = 0.75;
    const fadeOutOpacity = 0.0;

    /* Helper functions (https://jsfiddle.net/rjonean4/) */

    /* Handle fade animation on mouse over */
    function fade(opacity) {
        return function (d, i) {
            svg.selectAll("path.chord")
                .filter(function (d) { return d.source.index != i && d.target.index != i; })
                .transition()
                .style("opacity", opacity);
        };
    }

    /* Handle when a mouse enters a chord */
    function mouseonChord(d, i) {

        //Decrease opacity to all
        svg.selectAll("path.chord")
            .transition()
            .style("opacity", fadeOutOpacity);

        //Show hovered over chord with full opacity
        d3.select(this)
            .transition()
            .style("opacity", 1);

        //Define and show the tooltip over the mouse location
        // $(this).popover({
        //     //placement: 'auto top',
        //     title: 'test',
        //     placement: 'right',
        //     container: 'body',
        //     animation: false,
        //     offset: "20px -100px",
        //     followMouse: true,
        //     trigger: 'click',
        //     html: true,
        //     content: function () {
        //         return "<p style='font-size: 11px; text-align: center;'><span style='font-weight:900'>" +
        //             "</span> text <span style='font-weight:900'>" +
        //             "</span> folgt hier <span style='font-weight:900'>" + "</span> movies </p>";
        //     }
        // });
        // $(this).popover('show');
    }

    /* Handle when mouse leaves a chord; reset styles for all chords */
    function mouseoutChord(d) {
        //Hide the tooltip
        // $('.popover').each(function () {
        //     $(this).remove();
        // })
        //Set opacity back to default for all
        svg.selectAll("path.chord")
            .transition()
            .style("opacity", defaultOpacity);
    }

    /* Pre-process the data */
    let matrix = data.data;
    let names = data.names;
    let n = names.length;

    // Remove diagonal (photos with oneself)
    for (let i = 0; i < n; i++) {
        matrix[i][i] = 0;
    }

    /* Remove zero-valued participants */
    const threshold = 1;
    function sumRowAndCol(index) {
        let sum = 0;
        for (let i = 0; i < n; i++) {
            sum += matrix[index][i];
            sum += matrix[i][index];
        }
        return sum
    }
    let toDelete = [];
    for (let i = 0; i < n; i++) {
        const name = names[i];
        if (sumRowAndCol(i) <= threshold) {
            console.log(name + " below threshold; removing from matrix");
            toDelete.push(i);
        }
    }
    for (let i = toDelete.length - 1; i >= 0; i--) {
        toDeleteIndex = toDelete[i];
        
        /* Remove name */
        names.splice(toDeleteIndex, 1);

        /* Remove from matrix, first remove row, then column */
        matrix.splice(toDeleteIndex, 1);
        for (let r = 0; r < matrix.length; r++) {
            matrix[r].splice(toDeleteIndex, 1);
        }
    }

    /* Recompute variables */
    n = names.length;

    /* Establish graph size */
    let margin = { left: 90, top: 90, right: 90, bottom: 90 };
    let width = Math.min(window.innerWidth, 1000) - margin.left - margin.right;
    let height = Math.min(window.innerWidth, 1000) - margin.top - margin.bottom;
    let innerRadius = Math.min(width, height) * 0.4;
    let outerRadius = innerRadius + 10;

    /* Create d3 colors */
    let colors = d3.scaleOrdinal()
        .domain(d3.range(names.length))
        // .range(["#0B2547", "#942316", "#084594", "#7C9416", "#3A4700"]);
        .range(["#084594"]);

    /* Create chord */
    let chords = d3.chord()
        .padAngle(.03)
        .sortChords(d3.descending);

    /* Create arc that goes around the chord */
    let arcs = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

    /* Create paths that connect the arcs / chords */
    let paths = d3.ribbon()
        .radius(innerRadius);

    /* Create SVG area and apply matrix data to the chords */
    var svg = d3.select("#people-graph")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + (width / 2 + margin.left) + "," + (height / 2 + margin.top) + ")")
        .datum(chords(matrix));

    /* Draw outer arcs, grouped, with mouse interaction */
    let outerArcs = svg.selectAll("g.group")
        .data(function (chords) { return chords.groups; })
        .enter()
        .append("g")
        .attr("class", "group")
        .attr('title', (d) => { console.log("index = " + d.index + ", sum=" + sumRowAndCol(d.index)) })
        .on("mouseover", fade(fadeOutOpacity))
        .on("mouseout", fade(defaultOpacity))

    // text popups
    // .on("click", mouseonChord)
    // .on("mouseout", mouseoutChord);

    outerArcs.append("path")
        .style("fill", function (d) { return colors(d.index); })
        .attr("id", function (d, i) { return "group" + d.index; })
        .attr("d", arcs);

    /* Draw text labelling the names outside of the arcs */
    outerArcs.append("text")
        .each(function (d) { d.angle = (d.startAngle + d.endAngle) / 2; })
        .attr("dy", ".35em")
        .attr("class", "titles")
        .attr("text-anchor", function (d) { return d.angle > Math.PI ? "end" : null; })
        .attr("transform", function (d) {
            return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
                + "translate(" + (outerRadius + 10) + ")"
                + (d.angle > Math.PI ? "rotate(180)" : "");
        })
        .text(function (d, i) { return names[i]; });

    /* Draw the paths for inner chords */
    svg.selectAll("path.chord")
        .data(function (chords) { return chords; })
        .enter().append("path")
        .attr("class", "chord")
        .style("fill", function (d) { return colors(d.source.index); })
        .style("opacity", defaultOpacity)
        .attr("d", paths);
}