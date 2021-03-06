
final String PEOPLE_DATA_FILE = "../people_data.csv";
final String PEOPLE_INDEX_FILE = "../people_index.csv";

String[] people_names;

String[] date_names;
int[][] people_data;

PFont displayFont;

// Visualization type
final int VIS_PILL = 1;
final int VIS_DOTS = 2;

final int visualization_type = VIS_DOTS;

// Palettes
final int[] PALETTE_RAINBOW = {
    color(255, 0, 0),
    color(255, 180, 0),
    color(255, 255, 0),
    color(0, 255, 0),
    color(0, 255, 255),
    color(0, 80, 255),
    color(90, 0, 255),
    color(255, 0, 255)
};

final int[] PALETTE_PASTEL = {
    #9b5de5, #f15bb5, #f8a07b, #fee440,
    #7fd09d, #00bbf9, #00f5d4,
};

final int[] PALETTE_GREY = { #444444, #AAAAAA };

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

    // Remove people who are not active in the date range
    ArrayList ppl_idx_to_remove = new ArrayList();
    for (int i = 0; i < people_names.length; i++) {
        Boolean hasValues = false;

        for (int j = 0; j < dateCount; j++) {
            if (people_data[j][i] > 0) {
                hasValues = true;
                break;
            }
        }

        if (!hasValues) {
            ppl_idx_to_remove.add(i);
        }
    }

    // Given a list of ids to remove, remove them from both
    // people_names and people_data arrays
    final int new_ppl_count = people_names.length - ppl_idx_to_remove.size();
    String[] new_people_names = new String[new_ppl_count];
    int[][] new_people_data = new int[dateCount][new_ppl_count];

    int people_index = 0;
    for (int i = 0; i < people_names.length; i++) {
        if (ppl_idx_to_remove.contains(i)) {
            continue;
        }

        // Copy name
        new_people_names[people_index] = people_names[i];

        // Copy data
        for (int date_index = 0; date_index < dateCount; date_index++) {
            new_people_data[date_index][people_index] = people_data[date_index][i];
        }

        // Next new index
        people_index++;
    }

    // Replace
    people_names = new_people_names.clone();
    people_data = new_people_data.clone();
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
    final int i = x % PALETTE_RAINBOW.length;
    return PALETTE_RAINBOW[i];
}

PGraphics renderDataHD(int blockSize, float t, float scale) {


    final int gwidth = int(date_names.length * blockSize * scale);
    final int gheight = people_names.length * blockSize;

    final int padding = 80;
    final int namespace = 120;

    PGraphics pg = createGraphics(gwidth + (2 * padding) + namespace, gheight + (2 * padding));
    pg.beginDraw();
    pg.textFont(displayFont);

    pg.background(40);

    // Draw rect
    pg.fill(0);
    pg.rect(padding + namespace, padding, gwidth, gheight);
    pg.noStroke();

    // Draw vertical gridlines
    final int horizontal_spacing = 21;
    pg.stroke(40);
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
    pg.stroke(40);
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
                if (visualization_type == VIS_PILL) {
                    // opacity
                    final float opacity = constrain(map(val, 0, t, 30, 100), 0, 100);
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
                    final float opacity2 = constrain(map(val, 0, t, 70, 150), 0, 150);
                    final float y = padding + ppl_idx * blockSize;
                    final float randRange = 0.8 * blockSize;
                    final float randMultiplier = map(sqrt(val), 1, 10, 0, 1);
                    final float size = 16.0;
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
        pg.fill(rainbowize(ppl_idx));
        pg.text(people_names[ppl_idx], padding + namespace - 0.5 * blockSize, y);
    }

    pg.endDraw();
    return pg;
}

void settings() {
    // size(1280, 800);
}

// PImage img;

PGraphics pg;

void setup() {
    displayFont = createFont("Helvetica Neue", 14);

    readPeopleIndex();
    readPeopleData();

    // img = renderDataToImage(1, 1);
    // img.save("test.png");

    pg = renderDataHD(20, 5, 0.1);
    pg.save("test.png");
    exit();
}


void draw() {
    background(0);
    // scale(10);
    // image(img, map(mouseX, 0, width, 0, -date_names.length), 0);
    image(pg, map(mouseX, 0, width, 0, -pg.width), 0);
}
