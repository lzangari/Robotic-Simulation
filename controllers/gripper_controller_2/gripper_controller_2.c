/*
 * Controller for the large gripper of the world
 */
#include <webots/distance_sensor.h>
#include <webots/motor.h>
#include <webots/position_sensor.h>
#include <webots/robot.h>
#include <stdio.h>
#include <stdbool.h>


#define TIME_STEP 16

// Similar aprroach to girpper_1. Defining the states
enum State { WAITING, GRASPING, ROTATING, RELEASING, ROTATING_BACK, ROTATE_BELT };

// Step Function
static void step() {
	if (wb_robot_step(TIME_STEP) == -1) {
		wb_robot_cleanup();
	}
}

// Passive Wait helper Function
static void passive_wait(double sec) {
	double start_time = wb_robot_get_time();
	do {
		step();
	} while (start_time + sec > wb_robot_get_time());
}

// Main
int main(int argc, char **argv) {
	wb_robot_init();
	int counter = 3, i = 0; 
	int o = 0; // Object counter
	int state = WAITING; // Initial State
	
	// List of the target position of the objects on top of the pioneer
	const double object_target[3][6] = {
		{0.25, 1.63, -0.38, -1.55, -2.46, 0.865}, 
		{0, 1.63, -0.42, -2.25, -2.07, 0.0}, 
		{ 0, 1.63, -0.5, -1.57, -2.44, -0.75}
	};
	
	// List of the target position of the fingers
	const double finger_target[3][3] = {
		{0.9, 0.9, 0.35}, 
		{0.9, 0.9, 0.35}, 
		{0.9, 0.9, 0.33} };
	// Rotation speed
	double speed = 0.3;
	
	// Helper bool for controlling the arrival of the robots
           bool robot_arrived = false;

           // Initialize Joints and Fingers
	WbDeviceTag hand_motors[3];
	hand_motors[0] = wb_robot_get_device("finger_1_joint_1");
	hand_motors[1] = wb_robot_get_device("finger_2_joint_1");
	hand_motors[2] = wb_robot_get_device("finger_middle_joint_1");
	WbDeviceTag ur_motors[6];
	ur_motors[5] = wb_robot_get_device("shoulder_pan_joint");
	ur_motors[4] = wb_robot_get_device("shoulder_lift_joint");
	ur_motors[3] = wb_robot_get_device("elbow_joint");
	ur_motors[2] = wb_robot_get_device("wrist_1_joint");
	ur_motors[1] = wb_robot_get_device("wrist_2_joint");
	ur_motors[0] = wb_robot_get_device("wrist_3_joint");
            
           // Activate and set standard speed for joint and fingers
	for (i = 0; i < 6; ++i)
	{
		wb_motor_set_velocity(ur_motors[i], speed);
		wb_motor_set_position(ur_motors[i], 0.0);
	}

	for (i = 0; i < 3; ++i) 
	{
		wb_motor_set_position(hand_motors[i], 0.0);
		wb_motor_set_velocity(hand_motors[i], speed);
	}
            
           // Initialize Controlling Distance sensor 
	WbDeviceTag distance_sensor = wb_robot_get_device("distance sensor");
	wb_distance_sensor_enable(distance_sensor, TIME_STEP);

           // Initialize Controlling Floor Sensor
	WbDeviceTag floor_sensor = wb_robot_get_device("floor_sensor_1");
	wb_distance_sensor_enable(floor_sensor, TIME_STEP);
            
           // Initialize al the needed position sensor
	WbDeviceTag position_sensor = wb_robot_get_device("shoulder_pan_joint_sensor");
	WbDeviceTag position_sensor_finger = wb_robot_get_device("finger_middle_joint_1_sensor");
	WbDeviceTag position_sensor_schoulder_lift = wb_robot_get_device("shoulder_lift_joint_sensor");
	WbDeviceTag position_sensor_wrist_1 = wb_robot_get_device("wrist_1_joint_sensor");
	WbDeviceTag position_sensor_wrist_2 = wb_robot_get_device("wrist_2_joint_sensor");
	WbDeviceTag position_sensor_wrist_3 = wb_robot_get_device("wrist_3_joint_sensor");
	wb_position_sensor_enable(position_sensor, TIME_STEP);
	wb_position_sensor_enable(position_sensor_finger, TIME_STEP);
	wb_position_sensor_enable(position_sensor_schoulder_lift, TIME_STEP);
	wb_position_sensor_enable(position_sensor_wrist_1, TIME_STEP);
	wb_position_sensor_enable(position_sensor_wrist_2, TIME_STEP);
	wb_position_sensor_enable(position_sensor_wrist_3, TIME_STEP);


           // Main Loop: Just starts when the Floor sensors decets the arrival of the last robot.
           // Iterates trough the targets positions and puts the items on top of the belt for processing
	while (true) {
		step();
		
		double dist = wb_distance_sensor_get_value(floor_sensor);
		if (dist < 800 && robot_arrived != true)
		{
			robot_arrived = true;
			printf("dist %f \n", dist);
			printf("Making Movement \n");
		}
		
		if(o > 3)
		{
    		    wb_robot_cleanup();
    		    return 0;		
		}
		
		if (robot_arrived == true)
		{
			if (counter <= 0)
			{
				switch (state) {
				case WAITING:
					for (i = 0; i < 6; ++i)
					{
						wb_motor_set_position(ur_motors[i], object_target[o][i]);
					}
					printf("Rotating \n");
					state = ROTATING;
					break;
				case ROTATING:
					//Grasping Item
					passive_wait(8);
						printf("Grasping \n");
						state = GRASPING;
						for (i = 0; i < 3; ++i)
						{ 
							wb_motor_set_position(hand_motors[i], finger_target[o][i]);
						}
						o++;
					break;
				case GRASPING:
					//Rotate to belt
					passive_wait(4);
					printf("Rotating to belt \n");					
					for (i = 0; i < 6; ++i)
					{
						wb_motor_set_position(ur_motors[i], 0);
					}
					state = ROTATE_BELT;
					break;
				case ROTATE_BELT:
					//Releasing
					passive_wait(8);
					printf("Releasing \n");
					state = RELEASING;
					for (i = 0; i < 3; ++i)
					{
						wb_motor_set_position(hand_motors[i], 0);
					}
					break;
				case RELEASING:
					//Back to Init State
					passive_wait(5);
					printf("Rotating to initial state \n");
					for (i = 0; i < 6; ++i)
					{
						wb_motor_set_position(ur_motors[i], 0.0);
					}
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
		}
            };
	wb_robot_cleanup();
	return 0;
}




