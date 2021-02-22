/*
Controller for the first Grippers in the World
 */

#include <webots/distance_sensor.h>
#include <webots/motor.h>
#include <webots/position_sensor.h>
#include <webots/robot.h>
#include <stdio.h>

// Time Step of the world
#define TIME_STEP 32


// Step Function
static void step() {
  if (wb_robot_step(TIME_STEP) == -1) {
    wb_robot_cleanup();
  }
}

// A passive wait helper fuinction
static void passive_wait(double sec) {
  double start_time = wb_robot_get_time();
  do {
    step();
  } while (start_time + sec > wb_robot_get_time());
}

static 

// List of States of the grippers
enum State {WAITING, GRASPING, ROTATING, RELEASING, ROTATING_BACK};

// Main
int main(int argc, const char *argv[]) {
  /* necessary to initialize webots stuff */
  wb_robot_init();
  int counter = 0, i = 0;
  int state = WAITING;
  const double target_positions[] = {-1.88, -2.14, -2.38, -1.51};
  double speed = 0.5;
  // Depending on the imput values, the amount of finger grip can be definend depending on the incoming object
  double finger_motion[3] = {atof(argv[1]), atof(argv[2]), atof(argv[3])};

  // Initializes the fingers    
  WbDeviceTag hand_motors[3];
  hand_motors[0] = wb_robot_get_device("finger_1_joint_1");
  hand_motors[1] = wb_robot_get_device("finger_2_joint_1");
  hand_motors[2] = wb_robot_get_device("finger_middle_joint_1"); 
  
  // initializes the needed Joints
  WbDeviceTag ur_motors[4];
  ur_motors[0] = wb_robot_get_device("shoulder_lift_joint");
  ur_motors[1] = wb_robot_get_device("elbow_joint");
  ur_motors[2] = wb_robot_get_device("wrist_1_joint");
  ur_motors[3] = wb_robot_get_device("wrist_2_joint");
  
  // Sets initial speeds of hands and fingers
  for (i = 0; i < 4; ++i){
    wb_motor_set_velocity(ur_motors[i], speed);
    wb_motor_set_position(ur_motors[i], 0);
  }
    
  for (i = 0; i < 3; ++i){
    wb_motor_set_position(hand_motors[i], 0);
    wb_motor_set_velocity(hand_motors[i], speed*3);
    }

  // Initializes Distance sensors
  WbDeviceTag distance_sensor = wb_robot_get_device("distance sensor");
  wb_distance_sensor_enable(distance_sensor, TIME_STEP);
  // Initializes positions Sensors
  WbDeviceTag position_sensor = wb_robot_get_device("wrist_1_joint_sensor");
  wb_position_sensor_enable(position_sensor, TIME_STEP);


  /* main loop
   * Perform simulation steps of TIME_STEP milliseconds
   * and leave the loop when the simulation is over
   * Depending on the states, it changes the values of fingers and joints, and goes to 
   * a different state. The activation comes when the item is very near to the hand.
   * After delivering the item it returns to its position waiting for the next item
   */
  while (true) {
    step();
    if (counter <= 0) {
      switch (state) {
        case WAITING:
          if (wb_distance_sensor_get_value(distance_sensor) < 300) {          
            counter = 2;
            printf("Grasping \n");
            for (i = 0; i < 3; ++i){
              wb_motor_set_position(hand_motors[i], finger_motion[i]);
              }
            passive_wait(1); 
            state = GRASPING;
          }
          break;
        case GRASPING:
          for (i = 0; i < 4; ++i)
            wb_motor_set_position(ur_motors[i], target_positions[i]);
          printf("Rotating arm\n");
          state = ROTATING;
          break;
        case ROTATING:
          if (wb_position_sensor_get_value(position_sensor) < -2.3) {
            counter = 2;
            printf("Releasing \n");
            state = RELEASING;
            passive_wait(1); 
            for (i = 0; i < 3; ++i)
              wb_motor_set_position(hand_motors[i], 0);
          }
          break;
        case RELEASING:
          for (i = 0; i < 4; ++i)
            wb_motor_set_position(ur_motors[i], 0.0);
          printf("Rotating arm back\n");
          state = ROTATING_BACK;
          break;
        case ROTATING_BACK:
          if (wb_position_sensor_get_value(position_sensor) > -0.1) {
            state = WAITING;
            printf("Waiting \n");
          }
          break;
        }
      }
      counter--;
  };
  // Cleanup
  wb_robot_cleanup();
  return 0;
}
