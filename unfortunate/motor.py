import time

from pymata_aio.pymata3 import PyMata3


class Stepper:
    def __init__(self):
        self.board = PyMata3()
        self.steps_per_revolution = 32
        self.ratio = 64
        self.steps = self.steps_per_revolution * self.ratio
        self.pins = [8, 10, 9, 11]
        self.setup()

    def setup(self):
        '''
        Reset and configure the board. The sleeps are to give time for the messages to be sent.
        '''
        self.board.send_reset()
        time.sleep(2)
        self.board.stepper_config(self.steps, self.pins)
        time.sleep(2)

    def spin(self, spr=10, n=1):
        '''
        Spin the motor!
        :param spr: seconds per revolution
        :param n: number of revolutions to complete
        '''
        rps = 1 / spr
        rpm = int(rps * 60)
        time_per_step = spr / self.steps
        steps = int(self.steps * n)
        time_to_finish = steps * time_per_step
        self.board.stepper_step(rpm, steps)
        time.sleep(time_to_finish + 2)
        print(f'{n} revolution{"s" if n != 1 else ""} done in {time_to_finish}s')
