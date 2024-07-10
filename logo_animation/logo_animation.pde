int ydiff = 200;
int xdiff = 30;

int eyeshiftx = 0;
int eyeshifty = 0;

int shaking = 0;

int tick = 0;

PFont dotsfont;

void setup() {
  size(500, 500);
  background(0);
  dotsfont = createFont("./DotsAllForNow.ttf", 32);
  textFont(dotsfont);
}

boolean opening = true;

void draw() {
  background(0);
  stroke(255, 255, 255);
  fill(255, 255, 255);
  bezier(xdiff, 250, 250, 250 - ydiff, 250, 250 - ydiff, 500 - xdiff, 250);
  bezier(xdiff, 250, 250, 250 + ydiff, 250, 250 + ydiff, 500 - xdiff, 250);

  if (tick % 30 == 0) {
    eyeshiftx = (int)random(-50, 50);
    eyeshifty = (int)random(-50, 50);
  }

  tick++;

  noStroke();
  fill(255, 0, 0);
  circle(250 - eyeshiftx, 250 - eyeshifty, 180);

  fill(0, 0, 0);
  circle(250 - eyeshiftx * 1.5, 250 - eyeshifty * 1.5, 120);
  
  fill(255, 0, 0);
  textSize(50);
  text("X",250 - eyeshiftx*1.8 - 15, 250 - eyeshifty * 1.9 + 16, 180);
  if (tick % 30 == 0) {
    delay(500);
  }
}
