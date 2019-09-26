import time

from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants
import os


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
        duration = 0.2  # seconds
        freq = 880  # Hz
        os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
        print(f'{n} revolution{"s" if n != 1 else ""} done in {time_to_finish}s')


class Servo:
    def __init__(self, pin):
        self.board = PyMata3()
        self.pin = pin
        self.setup()

    def setup(self):
        self.board.send_reset()
        time.sleep(2)
        self.board.servo_config(self.pin)
        time.sleep(2)

    def spin(self, spr, n=1):
        step_size = 1
        sweep_size = 180
        time_per_step = (spr / (sweep_size / step_size)) * n
        for i in range(0, sweep_size, step_size):
            self.board.analog_write(self.pin, i)
            self.board.sleep(time_per_step)
        self.board.sleep(5)

