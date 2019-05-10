from threading import Thread

import click

from .camera import CanonCamera
from .motor import Stepper
from .process import Stream


@click.group(invoke_without_command=False)
def cli():
    pass


@cli.command()
@click.option('--length', '-l', default=10, help='The length of the video/rotation (in seconds).')
def video(length):
    '''
    Takes a video and spins the motor at the same time, then processes the frames of the video file.
    '''
    stepper = Stepper()

    def _shoot_and_process():
        with CanonCamera() as camera:
            path = camera.video(length)
        filestream = Stream(path)
        imgpath = filestream.process()
        click.echo(imgpath)

    def _spin():
        stepper.spin(length, 1.5)

    camera_thread = Thread(target=_shoot_and_process)
    camera_thread.start()
    _spin()
    camera_thread.join()


@cli.command()
@click.option('--frames', '-f', default=100,
              help='The number of frames to capture (also; the width of the final image).')
@click.option('--stream-port', default=2, help='The /dev/video device to read from.')
def stream(frames, stream_port):
    '''
    Uses the preview frames from a camera connected in USB mode to create the image. Requires
    additional setup; please see README for details.
    '''
    stepper = Stepper()
    videostream = Stream(stream_port)

    length = frames / videostream.framerate

    def _shoot_and_process():
        videostream.process(frames)

    def _spin():
        stepper.spin(length, 1.5)

    camera_thread = Thread(target=_shoot_and_process)
    camera_thread.start()
    _spin()
    camera_thread.join()
