import math
import os
import time
from threading import Thread

import click

from .camera import CanonCamera
from .motor import Servo, Stepper
from .process import Stream


@click.group(invoke_without_command=False)
def cli():
    pass


@cli.command()
@click.option('--length', '-l', default=10, help='The length of the video/rotation (in seconds).')
@click.option('--servo', is_flag=True, default=False, help='Use a servo instead of a stepper motor')
@click.option('--outputdir', '-o', default=os.getcwd(), help='')
@click.option('--rotation', '-r', default=0,
              help='angle (in degrees clockwise) of the camera from horizontal; will be rounded '
                   'to the nearest multiple of 90')
def video(length, servo, outputdir, rotation):
    '''
    Takes a video and spins the motor at the same time, then processes the frames of the video file.
    '''
    spinner = Stepper() if not servo else Servo(5)

    videodir = os.path.join(outputdir, 'videos')
    rawdir = os.path.join(outputdir, 'raw')
    croppeddir = os.path.join(outputdir, 'cropped')
    for d in [outputdir, videodir, rawdir, croppeddir]:
        if not os.path.exists(d):
            os.mkdir(d)

    def _shoot_and_process():
        with CanonCamera(videodir) as camera:
            path = camera.video(length)
        filestream = Stream(path, rawdir, rotation)
        imgpath = filestream.process()
        cropped_imgpath = filestream.crop()
        click.echo(cropped_imgpath)

    def _spin():
        spinner.spin(length, 2)

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
        spinner.spin(length, 2)

    camera_thread = Thread(target=_shoot_and_process)
    camera_thread.start()
    _spin()
    camera_thread.join()


@cli.command()
@click.argument('diameter', type=click.FLOAT)
@click.option('--focal-length', '-l', default=100, help='Focal length in mm')
@click.option('--frame-x', '-x', type=click.INT, default=720,
              help='Size of the image/frame across the x axis of the vial (i.e. width if shooting '
                   'landscape, height if portrait) in pixels')
@click.option('--sensor-x', '-s', default=24,
              help='Size of the sensor across the x axis of the vial (i.e. width if shooting '
                   'landscape, height if portrait) in mm')
@click.option('--ppmm', '-w', default=21,
              help='Approximate width of 1mm, in pixels, at the centre of rotation')
@click.option('--fps', '-r', default=60, help='Stream/video framerate')
def estimate(diameter, focal_length, frame_x, sensor_x, ppmm, fps):
    '''
    Estimate the optimum length of rotation in frames and seconds.
    '''
    frames = math.ceil((2 * math.pi * diameter * focal_length * frame_x * ppmm) / (
                (2 * focal_length * frame_x) - (diameter * sensor_x * ppmm)))
    t = round(frames / fps, 1)
    click.echo(f'''
    Try {t} seconds or {frames} frames:
    
    revile video --length {t}
    revile stream --frames {frames}
    ''')
