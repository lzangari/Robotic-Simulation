"""kuka_controller controller.
The Kuka waits for the receiver to get the signal to pick an item, then brings it to a shelf following a colored line
"""

from arm import Arm
from base import Base
from devices import Devices
from util import Util
from controller import Robot
import numpy as np

# create the Robot instance.
robot = Robot()
# Initialize the Robot´s devices
dev = Devices(robot)
# Initializes the Robot's base
base = Base(robot)
# Initializes the Robot's Util
util = Util(robot)
# Initialize Robot Parts
arm = Arm(robot)
# Initialize Camera
cam, width, height = dev.init_camera()
# Initialize the receiver
receiver = dev.init_receiver()

# Initialize the color to be followed, and the first color
COLORS = ["red", "blue", "yellow"]
color = 0
# Threshold of the different colors when looking for them
THRESHOLD = [219, 220, 219]
# Initial Direction
direction = "SOUTH"
# Initial State
actual_state = "WAITING_FOR_ITEM"
# Initial Arm Position
arm.set_position("RESET")

# Main loop:
# Depending on the State, the Kuka performs different Tasks and then changes its state to the next.
# This is performed in a cycle. The direction and the Item number are also tracked. The code Stops after three items,
# but can be expanded to work with n items in a cycle.
while True:
    util.step()
    if actual_state == "WAITING_FOR_ITEM":
        if color == 3:
            base.stop()
            break
        if receiver.getQueueLength() > 0:
            message = receiver.getData()
            if message.decode() == "pick_item":
                print("pick item")
                actual_state = "PICKING_ITEM"
            else:
                receiver.nextPacket()

    if actual_state == "PICKING_ITEM":
        if color > 2:
            base.stop()
        arm.set_position("PICK_ITEM")
        actual_state = "KEEPING_ITEM"

    if actual_state == "KEEPING_ITEM":
        arm.set_position("KEEP_ITEM")
        actual_state = "ROTATING"

    if actual_state == "ROTATING":
        base.rotate()
        max_color, _ = dev.evaluate_camera(COLORS[color], cam, width)
        max_black = dev.evaluate_camera("black", cam, width)
        if max_color >= THRESHOLD[color] and np.abs(max_black) > 160:
            actual_state = "FOLLOW_LINE"
            if direction == "NORTH":
                direction = "SOUTH"
            elif direction == "SOUTH":
                direction = "NORTH"
            base.set_max_speed()
        else:
            base.rotate()

    if actual_state == "FOLLOW_LINE":
        max_color, delta = dev.evaluate_camera(COLORS[color], cam, width)
        max_black = dev.evaluate_camera("black", cam, width)
        base.follow_line_wheel(delta)
        if max_black > 146:
            base.stop()
            if direction == "SOUTH":
                actual_state = "WAITING_FOR_ITEM"
                color += 1
            elif direction == "NORTH":
                # actual_state = "UNLOAD"
                base.stop()
                actual_state = "UNLOADING"

    if actual_state == "UNLOADING":
        arm.set_position("UNLOAD")
        arm.set_position("RESET")
        actual_state = "ROTATING"

    pass
# Enter here exit cleanup code.
