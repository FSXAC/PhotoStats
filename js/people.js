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

            // Sort by total
            peopleData.series.sort((a, b) => (a.total < b.total) ? 1 : ((b.total < a.total) ? -1 : 0))


            console.log(data);
            startRender();
        }
    });
});

// Global properties
const g = {
    bg_color: "#fff",
    border_width: 0,
    border_color: "#888",
    row_height: 16,
    date_width: 1 / 4,
    grid_color: "#ccc",
    name_margin: 140,
    padding: 0,
    dotsize: 5,
    line_color_dark: "#000",
    line_color_light: "#6baed6",
    truncate_top_people: 12,
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

function startRender() {

    const date_size = peopleData.dates.length;
    const people_size = (g.truncate_top_people > 0) ? g.truncate_top_people : peopleData.series.length;

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
        p.stroke(g.grid_color);
        for (let i = 0; i < people_size; i++) {
            const y = mapDataIndexToScreenCoords(0, i).y;
            p.line(0, y, p.width - 2 * g.padding, y);
        }

        p.noStroke();
        p.fill(255, 150);
        p.rect(0, 0, g.name_margin, p.height - 2 * g.padding);

        // Draw starting vertical line
        p.stroke(g.grid_color);
        p.line(g.name_margin, 0, g.name_margin, p.height - 2 * g.padding)

        p.pop();
    }

    function drawNames(p) {
        p.push();
        p.translate(g.padding, g.padding);
        p.fill(0);
        p.noStroke();
        p.textAlign(p.LEFT, p.CENTER);
        for (let i = 0; i < people_size; i++) {
            const name = peopleData.series[i].name + " (" + peopleData.series[i].total + ")";
            p.text(name, g.padding, mapDataIndexToScreenCoords(0, i).y);
        }
        p.pop();
    }

    const plotType = 'barcode';

    function plotPeopleData(p) {
        p.push();
        p.translate(g.padding + g.name_margin, g.padding);

        if (plotType === 'barcode') {
            p.strokeWeight(1);
            for (let i = 0; i < people_size; i++) {
                const name = peopleData.series[i].name;
                const personData = peopleData.series[i].values;

                for (let j = 0; j < personData.length; j++) {
                    const value = personData[j];
                    if (value == 0) {
                        continue;
                    }

                    let plot_pos = mapDataIndexToScreenCoords(j, i);
                    p.stroke(p.lerpColor(
                        p.color(g.line_color_light), p.color(g.line_color_dark), p.constrain(
                            p.map(value, 0, 50, 0, 1), 0, 1)));
                    const dy = 0.5 * g.row_height;
                    p.line(plot_pos.x, plot_pos.y - dy, plot_pos.x, plot_pos.y + dy);
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
            p.background(g.bg_color);


        }

        p.draw = () => {
            drawBorder(p);
            plotPeopleData(p);
            drawGrid(p);
            drawNames(p);
        }
    }

    let myp5 = new p5(sketch, document.getElementById('people-graph'));
}
