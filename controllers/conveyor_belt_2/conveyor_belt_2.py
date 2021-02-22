"""conveyor_belt_2 controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, Motor, DistanceSensor, Emitter
import struct

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())


def step():
    if (robot.step(timestep) == -1):
        pass


# Passive Wait Helepr
def passive_wait(seconds):
    start_time = robot.getTime()
    while True:
        step()
        if start_time + seconds < robot.getTime():
            break


belt_motor = robot.getMotor("linear_motor")
belt_motor.setPosition(float('inf'))

object_detector = robot.getDistanceSensor('object_detector')
object_detector.enable(timestep)

emitter = robot.getEmitter("emitter")
emitter.setChannel(1)



if belt_motor != 0:
    belt_motor.setVelocity(0.15)
else:
    print("Fatal Error: Motor needed for the conveyor belt not found")
    exit()


def run():
    sensor_value = object_detector.getValue()

    if sensor_value < 1000:
        emitter.send("pick_item".encode())
        belt_motor.setVelocity(0)
    else:
        emitter.send("waiting_for_item".encode())
        belt_motor.setVelocity(0.15)
    return


# Main loop:
# - perform simulation steps until Webots is stopping the controller
while True:
    step()
    run()
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
