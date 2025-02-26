#include <Arduino.h>
#include <ESP_I2S.h>

I2SClass I2S;


// put function declarations here:
int myFunction(int, int);

void setup() {
  // put your setup code here, to run once:
  int result = myFunction(2, 3);
  I2S.setPins(8, 7, 43, 44);
}

void loop() {
  // put your main code here, to run repeatedly:
}

// put function definitions here:
int myFunction(int x, int y) {
  return x + y;
}