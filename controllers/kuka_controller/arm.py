'''
Class for controlling the arm of the Kuka
'''

from util import Util
from base import Base


class Arm:
    def __init__(self, robot):

        self.robot = robot
        self.util = Util(self.robot)
        self.creep_forwards = [1, 1, 1, 1]
        self.creep_backwards = [-1, -1, -1, -1]
        self.iteration = 0  # Keeps track of the item
        self.base = Base(self.robot)

        # Initialize the arms
        self.arm1 = self.robot.getMotor('arm1')
        self.arm2 = self.robot.getMotor('arm2')
        self.arm3 = self.robot.getMotor('arm3')
        self.arm4 = self.robot.getMotor('arm4')
        self.arm5 = self.robot.getMotor('arm5')
        self.arms = [self.arm1, self.arm2, self.arm3, self.arm4, self.arm5]

        # Initialize the finger
        self.finger1 = self.robot.getMotor('finger1')
        self.finger2 = self.robot.getMotor('finger2')

        # Set Operation Velocity
        [arm.setVelocity(0.7) for arm in self.arms]
        self.finger1.setVelocity(0.03)
        self.finger2.setVelocity(0.03)

    # Helper Function for setting the position of all the arms
    def position_helper(self, position):
        i = 0
        for arm in self.arms:
            arm.setPosition(position[i])
            i += 1

    # Helper for Opening or closing the gripper
    def set_gripper(self, position):
        if position == "close":
            self.finger1.setPosition(0.01)
            self.finger2.setPosition(0.01)
        elif position == "open":
            self.finger1.setPosition(0.025)
            self.finger2.setPosition(0.025)

    # Pick Operation given an initial position.
    # Moves the Kuka forward, grips the item and moves it back to initial position
    def pick_helper(self, position):
        self.position_helper(position)
        self.util.passive_wait(4)
        self.base.set_speed(self.creep_forwards)
        self.util.passive_wait(4)
        self.base.stop()
        self.set_gripper("close")
        self.util.passive_wait(4)
        self.base.set_speed(self.creep_backwards)
        self.util.passive_wait(3)
        self.base.stop()

    # Item Deposition helper (similar to gripper)
    def deposit_helper(self, position):
        self.position_helper(position)
        self.util.passive_wait(4)
        self.base.set_speed(self.creep_forwards)
        self.util.passive_wait(4)
        self.base.stop()
        self.set_gripper("open")
        self.util.passive_wait(5)
        self.base.set_speed(self.creep_backwards)
        self.util.passive_wait(3)
        self.base.stop()
        self.iteration += 1

    # Set a position given the state. Some Position may differ depending on the item.
    # Iteration is used to know which item is currently picked or deposited
    def set_position(self, state):

        if state == "RESET":
            print("Resetting Arm Position")
            position = [0.0, 1.57, -2.635, 1.78, 0.0]
            self.position_helper(position)
            self.set_gripper("open")

        if state == "PICK_ITEM":
            print("Picking Item")
            if self.iteration == 0:
                position = [0, 1.05, -1.96, -0.50, 0]
                self.pick_helper(position)
            elif self.iteration == 1:
                position = [0.07, 1.05, -1.96, -0.50, 0]
                self.pick_helper(position)
            elif self.iteration == 2:
                position = [-0.07, 1.05, -1.96, -0.50, 0]
                self.pick_helper(position)

        if state == "KEEP_ITEM":
            position = [0, 1.57, -2.63, -0.39, 0]
            self.position_helper(position)
            print("Keeping Item")
            self.util.passive_wait(4)

        if state == "UNLOAD":
            print("Unloading Item")
            if self.iteration == 0:
                position = [0, 0.7, -1.6, -0.75, 0]
                self.deposit_helper(position)
            elif self.iteration == 1:
                position = [0, 0.7, -1.6, -0.65, 0]
                self.deposit_helper(position)
            elif self.iteration == 2:
                position = [0, 0.65, -1.6, -0.65, 0]
                self.deposit_helper(position)
