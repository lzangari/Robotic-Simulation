'''
Class for initializing and evaluation the Kuka devices
'''

from util import Util
from base import Base
from controller import Camera
import numpy as np


class Devices:
    def __init__(self, robot):
        self.robot = robot
        self.base = Base(robot)

    # Initializes the reciver
    def init_receiver(self):
        receiver = self.robot.getReceiver("receiver")
        receiver.enable(Util(self.robot).time_step())
        receiver.setChannel(1)
        return receiver

    # Initializes the camera
    def init_camera(self):
        cam = self.robot.getCamera("kuka_camera")
        cam.enable(Util(self.robot).time_step())
        width = cam.getWidth()
        height = cam.getHeight()
        return cam, width, height

    # Evaluates the camera: reads the value for red, yellow, blue and black. Depending on which line to follow,
    # it calculates the delta from its center
    def evaluate_camera(self, color, cam, width):
        red = list()
        yellow = list()
        blue = list()
        black = list()
        camera_data = cam.getImage()
        for pixel in range(0, width):
            red.append(255 - Camera.imageGetGreen(camera_data, width, pixel, 0))
            yellow.append(255 - Camera.imageGetBlue(camera_data, width, pixel, 0))
            blue.append(255 - Camera.imageGetRed(camera_data, width, pixel, 0))
            black.append(255 - Camera.imageGetRed(camera_data, width, pixel, 0)
                         - Camera.imageGetGreen(camera_data, width, pixel, 0)
                         - Camera.imageGetBlue(camera_data, width, pixel, 0))
        if color == "red":
            max_red = np.max(red)
            delta_red = np.where(red == np.max(red))[0][0] - (width / 2)
            return max_red, delta_red
        elif color == "blue":
            max_blue = np.max(blue)
            delta_blue = np.where(blue == np.max(blue))[0][0] - (width / 2)
            return max_blue, delta_blue
        elif color == "yellow":
            max_yellow = np.max(yellow)
            delta_yellow = np.where(yellow == np.max(yellow))[0][0] - (width / 2)
            return max_yellow, delta_yellow
        elif color == "black":
            max_black = np.max(black)
            return max_black
