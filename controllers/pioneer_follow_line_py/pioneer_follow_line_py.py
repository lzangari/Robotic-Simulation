"""
pioneer_follow_line_py controller.
This is the Main loop for the mouvment of all the pioneer Robot in the world
"""

from controller import *
from pioneer_helper import Helper
import numpy as np

# Create the Robot instance.
robot = Robot()
print(robot.getModel())
# Create a Helper Instance
helper = Helper(robot)
# Touch Sensor
touch_sensor = helper.init_touch_sensor()
# Camera
cam = helper.init_camera()
# Distance Sensors
sensors = helper.init_distance_sensor()
# Initialize the state and Direction
actual_state = "WAITING_FOR_ITEM"
direction = "Delivery"

# Main loop:
while True:
    helper.step()
    # State Evaluation
    if actual_state == "WAITING_FOR_ITEM":
        actual_state, speed = helper.waiting_for_item(touch_sensor)
        helper.move(speed)
        direction = "Delivery"

    if actual_state == "ROTATING":
        actual_state, speed = helper.rotating(cam)
        helper.move(speed)

    if actual_state == "FOLLOW_LINE":
        actual_state, speed = helper.follow_line(cam, sensors, direction)
        helper.move(speed)

    if actual_state == "WAITING_FOR_PICK":
        actual_state, speed = helper.waiting_for_pick(touch_sensor)
        helper.move(speed)
        direction = "Loading"

    pass

