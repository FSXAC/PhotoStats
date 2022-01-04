let peopleData;
let canvas;

$(document).ready(() => {
    $('.header-nav').load('navigation.html', () => {
        $('#nav-people-ridgeline').addClass('active');
    });

    $.ajax({
        type: "GET",
        url: "outdata/people_data.json",
        success: function (data) {
            peopleData = data;
            startRender();
        }
    });
});

// Global properties
let g = {
    bg_color: "#fff",
    border_width: 0,
    border_color: "#888",
    row_height: 20,
    bar_height: 16,
    date_width: 4,
    grid_color: "#eee",
    name_margin: 140,
    padding: 0,
    dotsize: 5,
    line_color_lighter: "#c6dbef",
    line_color_light: "#9ecae1",
    line_color_dark: "#084594",
    line_color_darker: "#000",
    truncate_top_people: 10,
    starting_date: "2021-01-01",
    convolve_data: false,
    convolution_size: 10,
    draw_hgrid: true,
    draw_vgrid: true,
    show_name_count: true,
    right_align_names: true
};

function calculateCanvasWidth(data_width) {
    return data_width * g.date_width + 2 *
        (g.border_width + g.padding) + g.name_margin;
}

function calculateCanvasHeight(data_height) {
    return (data_height + 1) * g.row_height + 2 * (
        g.border_width + g.padding
    );
}

function mapDataIndexToScreenCoords(date_index, person_index) {
    return {
        x: date_index * g.date_width,
        y: g.row_height * (person_index + 1)
    };
}

// Returns a list of indices where date ends with "-01"
function getMonthStartDateIndices(dates) {
    outList = [];
    for (let i = 0; i < dates.length; i++) {
        if (dates[i].endsWith('-01')) {
            outList.push(i);
        }
    }

    return outList;
}

function startRender() {

    // Filter / truncate data from dates
    if (g.starting_date) {

        // If specified starting date, try to find an index to truncate the date series
        const startIndex = peopleData.dates.indexOf(g.starting_date);

        if (startIndex != -1) {
            peopleData.dates = peopleData.dates.slice(startIndex, peopleData.dates.length);

            // Do the same for all person data (since parallel arrays)
            for (let j = 0; j < peopleData.series.length; j++) {
                peopleData.series[j].values = peopleData.series[j].values.slice(startIndex, peopleData.series[j].values.length);

                // Update sum
                peopleData.series[j].total = peopleData.series[j].values.reduce((a, b) => a + b, 0);
            }
        }
    }

    // Sort by total
    peopleData.series.sort((a, b) => (a.total < b.total) ? 1 : ((b.total < a.total) ? -1 : 0));

    // Filter / truncate data from top people
    if (g.truncate_top_people && g.truncate_top_people > 0) {
        peopleData.series = peopleData.series.slice(0, g.truncate_top_people);
    }

    // Filter out zero-valued series
    peopleData.series = peopleData.series.filter(person => person.total > 0);

    // Perform convultion on data if it's enabled
    const halfConvSize = Math.floor(g.convolution_size / 2);
    if (g.convolve_data && g.convolution_size >= 3) {
        for (let i = 0; i < peopleData.series.length; i++) {
            const valuesLength = peopleData.series[i].values.length;
            let newValues = Array(valuesLength);

            for (let j = 0; j < valuesLength; j++) {
                let start = j - halfConvSize;
                let end = j + halfConvSize;
                let sum = 0;

                for (let k = start; k < end; k++) {
                    if (k < 0 || k >= valuesLength ) {
                        continue;
                    }
                    sum += peopleData.series[i].values[k];
                }

                newValues[j] = sum / g.convolution_size;
            }

            // replace array
            peopleData.series[i].values = newValues;
        }
    }

    console.log(peopleData);

    // DONE processing data

    const date_size = peopleData.dates.length;
    const people_size = peopleData.series.length;

    console.log("Data loaded with " + date_size + " dates and " + people_size + " people");

    function drawBorder(p) {
        // p.stroke(g.border_color);
        // p.strokeWeight(1);
        // p.noFill();
        // p.rect(g.padding, g.padding, date_size, people_size);
    }

    function drawGrid(p) {
        p.push();
        p.translate(g.padding, g.padding);

        // Draw horizontal grid lines
        if (g.draw_hgrid) {
            p.stroke(g.grid_color);
            for (let i = 0; i < people_size; i++) {
                const y = mapDataIndexToScreenCoords(0, i).y;
                p.line(0, y, p.width - 2 * g.padding, y);
            }

            p.noStroke();
            p.fill(255, 150);
            p.rect(0, 0, g.name_margin, p.height - 2 * g.padding);
        }
        
        // Draw vertical grid lines
        if (g.draw_vgrid) {
            p.stroke(g.grid_color);
            p.noFill();
            p.translate(g.name_margin, 0);
            const dateIndices = getMonthStartDateIndices(peopleData.dates);
            for (let i = 0; i < dateIndices.length; i++) {
                const x = mapDataIndexToScreenCoords(dateIndices[i], 0).x;
                p.line(x, 0, x, p.height - 2 * g.padding);
            }
        }

        p.pop();
    }

    function drawNames(p) {
        p.push();
        p.translate(g.padding, g.padding);
        p.fill(0);
        p.noStroke();

        if (g.right_align_names) {
            p.textAlign(p.RIGHT, p.CENTER);
        } else {
            p.textAlign(p.LEFT, p.CENTER);
        }
        for (let i = 0; i < people_size; i++) {
            let name = peopleData.series[i].name
            if (g.show_name_count) {
                name += " (" + peopleData.series[i].total + ")";
            }

            const nameY = mapDataIndexToScreenCoords(0, i).y
            p.text(name, (g.right_align_names) ? g.name_margin - 10  : g.padding, nameY);
        }

        // Draw starting vertical line
        p.stroke(g.grid_color);
        p.line(g.name_margin, 0, g.name_margin, p.height - 2 * g.padding)
        p.pop();
    }

    const plotType = 'barcode';

    function plotPeopleData(p) {
        p.push();
        p.translate(g.padding + g.name_margin, g.padding);

        if (plotType === 'barcode') {

            // Type of fill
            if (g.date_width > 1) {
                p.noStroke();
            } else {
                p.strokeWeight(1);
            }

            // Size
            const dy = 0.5 * g.bar_height;

            // Plot it
            for (let i = 0; i < people_size; i++) {
                const personData = peopleData.series[i].values;

                for (let j = 0; j < personData.length; j++) {
                    const value = personData[j];
                    if (value == 0) {
                        continue;
                    }

                    let plot_pos = mapDataIndexToScreenCoords(j, i);
                
                    const valueColor = p.lerpColor(
                        p.color(g.line_color_lighter), p.color(g.line_color_dark), p.constrain(
                            p.map(value, 0, 20, 0, 1), 0, 1));

                    if (g.date_width > 1) {
                        p.fill(valueColor);
                        p.rect(plot_pos.x, plot_pos.y - dy, g.date_width, g.bar_height);
                    } else {
                        p.stroke(valueColor);
                        p.line(plot_pos.x, plot_pos.y - dy, plot_pos.x, plot_pos.y + dy);
                    }
                }
            }
        } else if (plotType === 'dot') {
            p.noStroke();
            p.blendMode(p.MULTIPLY);
            p.fill(p.color(g.line_color_light), 10);
            for (let i = 0; i < people_size; i++) {
                const name = peopleData.series[i].name;
                const personData = peopleData.series[i].values;

                for (let j = 0; j < personData.length; j++) {
                    const value = personData[j];
                    if (value == 0) {
                        continue;
                    }

                    const plot_pos = mapDataIndexToScreenCoords(j, i);
                    const size = g.dotsize + Math.log(value + 1);
                    p.ellipse(plot_pos.x, plot_pos.y, size, size);
                }
            }
        }

        p.pop();
    }

    const sketch = (p) => {

        // Setup canvas size from data size
        p.setup = () => {

            // Calculate canvas size based on config
            const canvas_width = calculateCanvasWidth(date_size);
            const canvas_height = calculateCanvasHeight(people_size);

            p.createCanvas(canvas_width, canvas_height);
            p.noLoop();

            // Draw border and clear screen
            // p.background(g.bg_color);


        }

        p.draw = () => {
            drawBorder(p);
            drawGrid(p);
            plotPeopleData(p);
            drawNames(p);
        }
    }

    let myp5 = new p5(sketch, document.getElementById('people-graph'));
}
