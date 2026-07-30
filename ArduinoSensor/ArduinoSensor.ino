#include <Arduino_LSM6DS3.h>

const float MOVEMENT_THRESHOLD = 0.4f;
const float RETURN_THRESHOLD = 0.25f;
const int STABLE_COUNT_NEEDED = 3;

enum HandState {
  NEUTRAL,
  MOVED_RIGHT,
  MOVED_LEFT
};

HandState currentState = NEUTRAL;
HandState previousState = MOVED_RIGHT;

int stableCount = 0;

void printState(HandState state) {
  switch (state) {
    case NEUTRAL:
      Serial.println("NEUTRAL");
      break;
    case MOVED_RIGHT:
      Serial.println("MOVED_RIGHT");
      break;
    case MOVED_LEFT:
      Serial.println("MOVED_LEFT");
      break;
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to init IMU.");
    while(1);
  }
  Serial.println("IMU is ready.");
}

void loop() {
  float ax, ay, az;

  // if (!IMU.accelerationAvailable()) {
  //   Serial.println("IMU Acceleration is unavailable.");
  //   return;
  // }

  IMU.readAcceleration(ax, ay, az);
  float tilt = ay;

  switch (currentState) {
    case NEUTRAL:
      if (tilt > MOVEMENT_THRESHOLD) {
        currentState = MOVED_RIGHT;
        stableCount = 0;
      }
      if (tilt < -MOVEMENT_THRESHOLD) {
        currentState = MOVED_LEFT;
        stableCount - 0;
      }
      break;
    case MOVED_RIGHT:
    case MOVED_LEFT:
      if (abs(tilt) < RETURN_THRESHOLD) {
        stableCount++;
        if (stableCount >= STABLE_COUNT_NEEDED) {
          currentState = NEUTRAL;
          stableCount = 0;
        }
      }
      else {
        stableCount = 0;
      }
      break;
    default:
      break;
  }
  
  if (currentState != previousState) {
    printState(currentState);
    previousState = currentState;
  }

  delay(0);
}
