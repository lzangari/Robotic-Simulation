"""
Helper Functions for the mouvment and Initialization of the Pioneer Robots
"""
from controller import Camera
import numpy as np

class Helper:
    def __init__(self, robot):

        # Robot Proprieties
        self.robot = robot
        self.timestep = int(robot.getBasicTimeStep())
        self.MAX_SENSOR_NUMBER = 16
        self.MAX_SPEED = 5.24
        self.STATES = ["WAITING_FOR_ITEM", "FOLLOW_LINE", "WAITING_FOR_PICK", "ROTATING"]

        # Wheels
        self.left_wheel = robot.getMotor("left wheel")
        self.right_wheel = robot.getMotor("right wheel")
        self.left_wheel.setPosition(float('inf'))
        self.right_wheel.setPosition(float('inf'))
        self.left_wheel.setVelocity(0.0)
        self.right_wheel.setVelocity(0.0)

        # Set Initial Speed
        self.speed = [0.0, 0.0]

        # Camera
        self.width = 0

    # World Step
    def step(self):
        if self.robot.step(self.timestep) == -1:
            pass

    # Passive Wait
    def passive_wait(self, seconds):
        start_time = self.robot.getTime()
        while True:
            self.step()
            if start_time + seconds < self.robot.getTime():
                break

    # Initialize Touch sensors
    def init_touch_sensor(self):
        # Touch Sensor
        touch_sensor = self.robot.getTouchSensor("pressureSensor")
        touch_sensor.enable(self.timestep)
        return touch_sensor

    # Initialize the camera
    def init_camera(self):
        # Camera
        cam = self.robot.getCamera("pioneer_camera")
        cam.enable(self.timestep)
        self.width = cam.getWidth()
        return cam

    # Initialize the distance Sensors
    def init_distance_sensor(self):
        # Distance Sensors
        sensors = []
        for s in range(self.MAX_SENSOR_NUMBER):
            sensors.append(self.robot.getDistanceSensor("so{}".format(s)))
            sensors[s].enable(self.timestep)
        return sensors

    # Helper Function when wating for Item
    def waiting_for_item(self, touch_sensor):
        state = self.STATES[0]
        self.speed[0] = self.speed[1] = 0
        force_value = touch_sensor.getValue()
        if force_value > 4:
            print("Detected Pressure: {}. Waiting 3 seconds...".format(force_value))
            self.passive_wait(3)
            state = "ROTATING"
            self.speed[0] = self.speed[1] = self.MAX_SPEED
            return state, self.speed
        else:
            return state, self.speed

    # Helper Function when rotationg
    def rotating(self, cam):
        gray = []
        state = "ROTATING"
        camera_data = cam.getImage()
        for pixel in range(0, self.width):
            gray.append(Camera.imageGetGray(camera_data, self.width, pixel, 0))

        if np.amin(gray) < 50:
            state = "FOLLOW_LINE"
            self.speed[0] = self.MAX_SPEED
            self.speed[1] = self.MAX_SPEED
        else:
            self.speed[0] = self.MAX_SPEED
            self.speed[1] = -self.MAX_SPEED

        return state, self.speed

    # Helper Function when Following the line (collision avoidance)
    def follow_line(self, cam, sensors, direction):
        gray = []
        red = []
        state = "FOLLOW_LINE"
        camera_data = cam.getImage()
        for pixel in range(0, self.width):
            gray.append(Camera.imageGetGray(camera_data, self.width, pixel, 0))
            red.append(Camera.imageGetGreen(camera_data, self.width, pixel, 0))

        for sensor in range(2, 6):
            if sensors[sensor].getValue() > 950:
                self.speed[0] = self.speed[1] = 0
                return state, self.speed

        min_red = np.min(red)
        delta_gray = np.where(gray == np.amin(gray))[0][0] - (self.width / 2)
        if np.abs(delta_gray) > 4:
            self.speed[0] = self.MAX_SPEED + (delta_gray / 4)
            self.speed[1] = self.MAX_SPEED - (delta_gray / 4)
        else:
            self.speed[0] = self.MAX_SPEED
            self.speed[1] = self.MAX_SPEED

        if min_red > 194 and direction == "Delivery":
            self.speed[0] = self.speed[1] = 0
            state = "WAITING_FOR_PICK"
        elif min_red > 194 and direction == "Loading":
            state = "WAITING_FOR_ITEM"
            self.speed[0] = self.speed[1] = 0

        return state, self.speed

    # Helper Function when waiting for the item to be picked up
    def waiting_for_pick(self, touch_sensor):
        state = "WAITING_FOR_PICK"
        self.speed[0] = self.speed[1] = 0
        self.passive_wait(3)
        force_value = touch_sensor.getValue()
        if force_value < 2.7:
            self.passive_wait(3)
            print("Detected Pick. Waiting 3 seconds...")
            state = "ROTATING"
        return state, self.speed

    # Main move function for changing the wheel speed
    def move(self, speed):
        self.left_wheel.setVelocity(speed[0])
        self.right_wheel.setVelocity(speed[1])

