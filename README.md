This is a simple example package for generating 2D images of cylindrical surfaces, using the principal of _rollout photography_ or _slit scanning_.

This package has two major functions: _capturing_ new videos, and _processing_ video streams.
It can also be used in two forms: as a command line interface (CLI), or as a Python package. The [CLI script](revile/cli.py) shows examples of how it can be used in your own Python scripts.

## 0. Installation

### 0.1 Requirements
1. [Python 3.6+](https://www.python.org)

The code has only been tested and confirmed to work on a Linux OS, but it may work on others.

### 0.2 Setup
Install using pip:

```sh
pip install git+git://github.com/NaturalHistoryMuseum/revile.git#egg=revile
```

## 1. Capturing

### 1.1 Requirements

#### 1.1.1 Software requirements
1. [gphoto2](https://github.com/gphoto/gphoto2)
2. [sox](http://sox.sourceforge.net) (optional - for playing a beep to signal end of turntable movement)
3. [v4l2loopback](https://github.com/umlaeute/v4l2loopback) (optional - for using cameras other than new Canon DSLRs)
4. [ffmpeg](https://ffmpeg.org) (optional - for using cameras other than new Canon DSLRs)

#### 1.1.2 Equipment requirements
1. Arduino Uno
2. Servo _or_ stepper motor + driver (with secure flat surface attached to act as a turntable)
   - originally developed with a 28BYJ-48 stepper motor and ULN2003 driver
3. Camera
   - some parts will only work with newer Canon DSLRs, others can use anything connected as a webcam

### 1.2 Camera setup
1. Set up the shot; e.g. point the camera at the object, focus it, etc.
2. Connect the camera to the computer and turn it on.

#### 1.2.1 New Canon DSLRs
- insert an SD card, preferably a high-speed one (it may not work with a lower-speed one)
- set to video mode
- configure the desired video settings on the camera (e.g. 60fps vs 30fps)

#### 1.2.2 Other cameras
The camera needs to be streaming from a `/dev/video` device. This may not be possible with all cameras; check your specifications.
For a camera connected via USB with a preview mode available, you can do this using `v4l2loopback`. After installing `v4l2loopback`:

```sh
modprobe v4l2loopback
find /dev -name 'video*' | sort | tail -n 1  # to find the device
gphoto2 --stdout --capture-movie | ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -threads 8 -r 60 -f v4l2 /dev/video[DEVICE NUMBER HERE]
```

### 1.3 Object setup
1. Connect the servo/motor + driver and Arduino
2. Plug the Arduino into the computer via USB
3. Fix the subject securely onto the turntable.

## 1.4 Usage

### 1.4.1 Canon mode
```sh
revile video --help

Usage: revile video [OPTIONS]

  Takes a video and spins the motor at the same time, then processes the
  frames of the video file.

Options:
  -l, --length INTEGER    The length of the video/rotation (in seconds).
  --servo                 Use a servo instead of a stepper motor
  -o, --outputdir TEXT
  -r, --rotation INTEGER  angle (in degrees clockwise) of the camera from
                          horizontal; will be rounded to the nearest multiple
                          of 90
```

e.g. to create and process a 20s video, then save it in `/data/videos`:
```sh
revile video --length 20 --outputdir /data/videos
```

### 1.4.2 Webcam mode
```sh
revile stream --help

Usage: revile stream [OPTIONS]

  Uses the preview frames from a camera connected in USB mode to create the
  image.

Options:
  -f, --frames INTEGER   The number of frames to capture (also; the width of
                         the final image).
  --stream-port INTEGER  The /dev/video device to read from.
  --servo                Use a servo instead of a stepper motor
```

e.g. to create and process 500 frames using device `/dev/video1`:
```sh
revile stream --frames 500 --stream-port 1
```

### 1.4.3 'Estimate' utility
```sh
revile estimate --help

Usage: revile estimate [OPTIONS] DIAMETER

  Estimate the optimum length of rotation in frames and seconds.

Options:
  -l, --focal-length INTEGER  Focal length in mm
  -x, --frame-x INTEGER       Size of the image/frame across the x axis of the
                              vial (i.e. width if shooting landscape, height
                              if portrait) in pixels
  -s, --sensor-x INTEGER      Size of the sensor across the x axis of the vial
                              (i.e. width if shooting landscape, height if
                              portrait) in mm
  -w, --ppmm INTEGER          Approximate width of 1mm, in pixels, at the
                              centre of rotation
  -r, --fps INTEGER           Stream/video framerate
```

e.g. at a focal length of 100mm, frame width of 720px, sensor width of 24mm, 1mm width of 21px, and framerate of 60fps, for a 20mm vial:
```sh
revile estimate -l 100 -x 720 -s 24 -w 21 -r 60 20

    Try 23.6 seconds or 1419 frames:
    
    revile video --length 23.6
    revile stream --frames 1419
```

## 2. Processing

### 2.1 Requirements
There are no additional requirements for processing video files/streams.

### 2.2 Usage
```sh
revile process --help

Usage: revile process [OPTIONS] FILEPATH

Options:
  -r, --rotate INTEGER  angle (in degrees clockwise) of the image from
                        horizontal; will be rounded to the nearest multiple of
                        90

  -o, --outputdir TEXT  A directory to save the files to
```

e.g. to process `examplevideo.mov`, shot in portrait orientation, and output to `/data/revile/`:
```sh
revile process examplevideo.mov -r 270 -o /data/revile 
```
