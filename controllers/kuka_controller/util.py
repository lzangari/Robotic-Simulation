'''
Util Class for the Kuka Robot. Here the World's Step can be controlled
'''
class Util:
    def __init__(self, robot):
        self.robot = robot

    def time_step(self):
        timestep = int(self.robot.getBasicTimeStep())
        return timestep

    # The Step of the World
    def step(self):
        if (self.robot.step(self.time_step()) == -1):
            pass

    # Passive Wait Helepr
    def passive_wait(self, seconds):
        start_time = self.robot.getTime()
        while True:
            self.step()
            if start_time + seconds < self.robot.getTime():
                break
