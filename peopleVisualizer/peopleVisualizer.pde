
final String PEOPLE_DATA_FILE = "../people_data.csv";
final String PEOPLE_INDEX_FILE = "../people_index.csv";

String[] people_names;
// parallel list to keep track if drawn
Boolean[] people_drawn;

String[] date_names;
int[][] people_data;

PFont displayFont;

// Visualization type
final int VIS_PILL = 1;
final int VIS_DOTS = 2;

final int visualization_type = VIS_DOTS;

void readPeopleIndex() {
    Table table = loadTable(PEOPLE_INDEX_FILE, "header");
    people_names = new String[table.getRowCount()];
    int index = 0;
    for (TableRow row : table.rows()) {
        people_names[index++] = row.getString("name");
    }
}

void readPeopleData() {
    Table table = loadTable(PEOPLE_DATA_FILE, "header");
    final int dateCount = table.getRowCount();

    date_names = new String[dateCount];
    people_data = new int[dateCount][people_names.length];
    
    int index = 0;
    
    for (TableRow row : table.rows()) {
        String date_name = row.getString("date");
        date_names[index] = date_name;

        for (int i = 0; i < people_names.length; i++) {
            int val = row.getInt(str(i));
            if (val != 0) {
                people_data[index][i] = val;
            }
        }

        index++;
    }
}

PImage renderDataToImage(int shrink, float t) {
    final int w = date_names.length;
    final int h = people_names.length;
    PImage img = createImage(w, h, RGB);

    img.loadPixels();
    
    for (int day_idx = 0; day_idx < w; day_idx++) {
        for (int ppl_idx = 0; ppl_idx < h; ppl_idx++) {
            int val = people_data[day_idx][ppl_idx];
            if (val > 0) {
                float c = constrain(map(val, 0, t, 0, 255), 0, 255);
                if (ppl_idx == 9) {
                    img.pixels[ppl_idx * w + day_idx] += color(c, 0, 0);
                } else {
                    img.pixels[ppl_idx * w + day_idx] += color(c, c, c);
                }
            }
        }
    }
    img.updatePixels();
    return img;
}

// TODO: support palettes
color rainbowize(int x) {
    switch (x % 8) {
        case 0: return color(255, 0, 0);
        case 1: return color(255, 180, 0);
        case 2: return color(255, 255, 0);
        case 3: return color(0, 255, 0);
        case 4: return color(0, 255, 255);
        case 5: return color(0, 80, 255);
        case 6: return color(90, 0, 255);
        case 7: return color(255, 0, 255);
    }
    
    return color(0, 0, 0);
}

PGraphics renderDataHD(int blockSize, float t, float scale) {


    final int gwidth = int(date_names.length * blockSize * scale);
    final int gheight = people_names.length * blockSize;

    final int padding = 80;
    final int namespace = 120;

    PGraphics pg = createGraphics(gwidth + (2 * padding) + namespace, gheight + (2 * padding));
    pg.beginDraw();
    pg.textFont(displayFont);

    pg.background(20);

    // Draw rect
    pg.fill(0);
    pg.rect(padding + namespace, padding, gwidth, gheight);
    pg.noStroke();

    // Draw vertical gridlines
    final int horizontal_spacing = 21;
    pg.stroke(20);
    pg.strokeWeight(1);
    for (int day_idx = 0; day_idx < date_names.length; day_idx += horizontal_spacing) {
        float x = padding + namespace + day_idx * blockSize * scale;
        pg.line(x, padding, x, pg.height - padding);
    }
    pg.noStroke();

    // Draw dates
    pg.textAlign(CENTER, BOTTOM);
    pg.fill(120);
    String prevYear = "";
    for (int day_idx = 0; day_idx < date_names.length; day_idx += horizontal_spacing) {
        float x = padding + namespace + day_idx * blockSize * scale;
        pg.text(date_names[day_idx].substring(5, 10), x, padding - 5);

        String year = date_names[day_idx].substring(0, 4);
        if (prevYear.equals(year) == false) {
            pg.textSize(20);
            pg.fill(200);
            pg.text(year, x, padding - blockSize);
            pg.textSize(14);
            pg.fill(120);
            prevYear = year;
        }
    }

    // Draw horizontal lines
    // final int vertical_spacing = 4;
    final int vertical_spacing = 1;
    pg.stroke(20);
    for (int ppl_idx = 0; ppl_idx < people_names.length; ppl_idx += vertical_spacing) {
        float y = padding + ppl_idx * blockSize + 0.5 * blockSize;
        pg.line(padding + namespace, y, gwidth + padding + namespace, y);
    }
    pg.noStroke();

    // Draw dots
    pg.blendMode(ADD);
    for (int day_idx = 0; day_idx < date_names.length; day_idx++) {

        float x = padding + namespace + day_idx * blockSize * scale;

        for (int ppl_idx = 0; ppl_idx < people_names.length; ppl_idx++) {
            int val = people_data[day_idx][ppl_idx];
            if (val > 0) {
                people_drawn[ppl_idx] = true;

                if (visualization_type == VIS_PILL) {
                    // opacity
                    final float opacity = constrain(map(val, 0, t, 70, 150), 0, 255);
                    //float opacity = 200;

                    // size 
                    //float r = constrain(map(val, 1, t, 3, blockSize), 3, 2 * blockSize);
                    //float r = blockSize;
                    float r = map(val, 1, t, 3, blockSize);
                    float y = padding + ppl_idx * blockSize;

                    //pg.fill(rainbowize(ppl_idx), opacity);
                    //pg.ellipse(x + blockSize / 2, y + blockSize / 2, r, r);
                    pg.stroke(rainbowize(ppl_idx), opacity);
                    pg.strokeWeight(r);
                    pg.line(x - blockSize, y + blockSize / 2, x + blockSize, y + blockSize/2);
                } else if (visualization_type == VIS_DOTS) {
                    final float opacity1 = 70;
                    final float opacity2 = constrain(map(val, 0, t, 70, 150), 0, 255);
                    final float y = padding + ppl_idx * blockSize;
                    final float randRange = blockSize;
                    final float randMultiplier = map(sqrt(val), 1, 10, 0, 1);
                    final float size = 20.0;
                    final float size2 = 4.0;

                    for (int v = 0; v < val; v++) {
                        pg.noStroke();
                        pg.fill(rainbowize(ppl_idx), opacity1);

                        float dx = x + random(-randRange, randRange);
                        float dy = y + blockSize / 2 + random(-randRange, randRange) * randMultiplier;
                        pg.ellipse(dx, dy, size, size);

                        pg.fill(255, opacity2);
                        pg.ellipse(dx, dy, size2, size2);
                    }
                }
            }
        }
    }
    pg.blendMode(BLEND);

    // draw names
    pg.textAlign(RIGHT, CENTER);
    for (int ppl_idx = 0; ppl_idx < people_names.length; ppl_idx++) {
        float y = padding + ppl_idx * blockSize + 0.5 * blockSize;
        pg.fill(rainbowize(ppl_idx), people_drawn[ppl_idx] ? 255 : 20);
        pg.text(people_names[ppl_idx], padding + namespace - 0.5 * blockSize, y);
    }

    pg.endDraw();
    return pg;
}

void settings() {
    size(1280, 800);
}

// PImage img;

PGraphics pg;

void setup() {
    displayFont = createFont("Helvetica Neue", 14);

    readPeopleIndex();
    readPeopleData();
    people_drawn = new Boolean[people_names.length];
    for (int i = 0; i < people_names.length; i++) {
        people_drawn[i] = false;
    }

    // img = renderDataToImage(1, 1);
    // img.save("test.png");

    pg = renderDataHD(30, 5, 0.15);
    pg.save("test.png");
    exit();
}


void draw() {
    background(0);
    // scale(10);
    // image(img, map(mouseX, 0, width, 0, -date_names.length), 0);
    image(pg, map(mouseX, 0, width, 0, -pg.width), 0);
}
