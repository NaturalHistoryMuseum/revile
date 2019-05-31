from threading import Thread
import time
import click
import math

from .camera import CanonCamera
from .motor import Stepper, Servo
from .process import Stream


@click.group(invoke_without_command=False)
def cli():
    pass


@cli.command()
@click.option('--length', '-l', default=10, help='The length of the video/rotation (in seconds).')
@click.option('--servo', is_flag=True, default=False, help='Use a servo instead of a stepper motor')
def video(length, servo):
    '''
    Takes a video and spins the motor at the same time, then processes the frames of the video file.
    '''
    spinner = Stepper() if not servo else Servo(5)

    def _shoot_and_process():
        with CanonCamera() as camera:
            path = camera.video(length)
        filestream = Stream(path)
        imgpath = filestream.process()
        click.echo(imgpath)

    def _spin():
        spinner.spin(length, 1.5)

    camera_thread = Thread(target=_shoot_and_process)
    camera_thread.start()
    _spin()
    camera_thread.join()


@cli.command()
@click.option('--frames', '-f', default=100,
              help='The number of frames to capture (also; the width of the final image).')
@click.option('--stream-port', default=2, help='The /dev/video device to read from.')
@click.option('--servo', is_flag=True, default=False, help='Use a servo instead of a stepper motor')
def stream(frames, stream_port, servo):
    '''
    Uses the preview frames from a camera connected in USB mode to create the image. Requires
    additional setup; please see README for details.
    '''
    spinner = Stepper() if not servo else Servo(5)
    videostream = Stream(stream_port)

    length = frames / videostream.framerate

    def _shoot_and_process():
        time.sleep(1)
        videostream.process(frames)

    def _spin():
        spinner.spin(length, 1.5)

    camera_thread = Thread(target=_shoot_and_process)
    camera_thread.start()
    _spin()
    camera_thread.join()


@cli.command()
@click.argument('diameter', type=click.FLOAT)
@click.option('--ppm', default=21)
@click.option('--fps', default=60)
def estimate(diameter, ppm, fps):
    circumference = math.pi * diameter
    pixels = circumference * ppm
    seconds = pixels / fps
    click.echo(f'''
    Try {int(seconds)} seconds:
    
    unfortunate video --length {int(seconds)}
    ''')