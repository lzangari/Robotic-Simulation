'''
Class for the Controll of the base (wheels) of the Kuka Robot
'''

import numpy as np


class Base:

    def __init__(self, robot):
        self.robot = robot
        self.wheel1 = self.robot.getMotor('wheel1')
        self.wheel2 = self.robot.getMotor('wheel2')
        self.wheel3 = self.robot.getMotor('wheel3')
        self.wheel4 = self.robot.getMotor('wheel4')
        self.wheels = [self.wheel1, self.wheel2, self.wheel3, self.wheel4]
        self.max_speed = 5.0

    # Sets the sped of the for wheels
    def set_speed(self, speed):
        i = 0
        for wheel in self.wheels:
            wheel.setPosition(float('inf'))
            wheel.setVelocity(speed[i])
            i += 1

    # Sets all the wheel to max speed
    def set_max_speed(self):
        speed = [5.0, 5.0, 5.0, 5.0]
        self.set_speed(speed)

    # Stops all wheels
    def stop(self):
        speed = [0, 0, 0, 0]
        self.set_speed(speed)

    # Rotate to the left
    def rotate(self):
        speed = [self.max_speed, -self.max_speed, self.max_speed, -self.max_speed]
        self.set_speed(speed)

    # Speed Control while following a line. Given a delta from the center, it steers to the left or right if the delta
    # is too big, otherwise it goes straight
    def follow_line_wheel(self, delta):
        if np.abs(delta) > 6:
            speed = [- delta / 3, delta / 3, -delta / 3, delta / 3]
            self.set_speed(speed)
        else:
            [wheel.setVelocity(self.max_speed) for wheel in self.wheels]
