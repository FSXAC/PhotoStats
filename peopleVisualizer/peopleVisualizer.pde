
final String PEOPLE_DATA_FILE = "../people_data.csv";
final String PEOPLE_INDEX_FILE = "../people_index.csv";

String[] people_names;
String[] date_names;
int[][] people_data;

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
    pg.background(20);
    pg.fill(0);
    pg.rect(padding + namespace, padding, gwidth, gheight);
    pg.noStroke();

    pg.stroke(80);
    pg.strokeWeight(1);
    for (int day_idx = 0; day_idx < date_names.length; day_idx += 30) {
        float x = padding + namespace + day_idx * blockSize * scale;
        pg.line(x, padding, x, pg.height - padding);
    }
    pg.noStroke();

    pg.textAlign(CENTER, BOTTOM);
    pg.fill(150);
    for (int day_idx = 0; day_idx < date_names.length; day_idx += 30) {
        float x = padding + namespace + day_idx * blockSize * scale;
        pg.text(date_names[day_idx], x, padding - 0.5 * blockSize);
    }

    pg.textAlign(RIGHT, CENTER);
    for (int ppl_idx = 0; ppl_idx < people_names.length; ppl_idx++) {
        float y = padding + ppl_idx * blockSize + 0.5 * blockSize;
        pg.fill(rainbowize(ppl_idx));
        pg.text(people_names[ppl_idx], padding + namespace - blockSize, y);

        if (ppl_idx % 8 == 0) {
            pg.stroke(30);
            pg.line(padding + namespace, y, gwidth + padding + namespace, y);
            pg.noStroke();
        }
    }

    // Draw dots
    for (int day_idx = 0; day_idx < date_names.length; day_idx++) {

        float x = padding + namespace + day_idx * blockSize * scale;

        for (int ppl_idx = 0; ppl_idx < people_names.length; ppl_idx++) {
            int val = people_data[day_idx][ppl_idx];
            if (val > 0) {
                // opacity
                final float opacity = constrain(map(val, 0, t, 50, 100), 0, 255);

                // size 
                float r = constrain(map(val, 1, t, 3, blockSize), blockSize/2, blockSize);
                float y = padding + ppl_idx * blockSize;

                pg.fill(rainbowize(ppl_idx), opacity);
                pg.ellipse(x + blockSize / 2, y + blockSize / 2, r, r);
            }
        }
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
    readPeopleIndex();
    readPeopleData();

    // img = renderDataToImage(1, 1);
    // img.save("test.png");

    pg = renderDataHD(20, 5, 0.2);
    pg.save("test.png");
    exit();
}


void draw() {
    background(0);
    // scale(10);
    // image(img, map(mouseX, 0, width, 0, -date_names.length), 0);
    image(pg, map(mouseX, 0, width, 0, -pg.width), 0);
}
