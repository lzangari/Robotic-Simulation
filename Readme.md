# Robotic Simulation


A Simulated quality control module for a toy factory using  Cyberbotics [Webots](https://cyberbotics.com/).
Proiduced rubber ducks are automatically picked up and transported to a quality check area by autonomous 3-Wheeld robots that follow a line on the ground. Here they are picked up again, controlled, and then transported to the packing area by a [Kuka](https://www.kuka.com/de-de/produkte-leistungen/robotersysteme/industrieroboter) one armed robot.

## Controllers

The running belts are controlled with Python (conveyor_belt_2.py), while the gripper are controlled with C. The Kuka robot and the line following pioneer robots are controlled with python controllers.

## Video

A video of the results can be found [here](https://www.youtube.com/watch?v=OT6dlrk56P0&feature=youtu.be).
