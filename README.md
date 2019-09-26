This is a simple example package for slit scanning using a (fairly new) Canon DSLR and a 28BYJ-48 stepper motor.

## Installing
At the moment this will only run on Python 3.6+, but it can probably be adapted.

```sh
pip install git+git://github.com/alycejenni/revile.git#egg=revile
```

I have no idea if this works on anything but Linux.

## Usage

### Materials

- 28BYJ-48 stepper motor
- ULN2003 driver
- Arduino Uno
- camera (some parts will only work with newer Canon DSLRs, others can use anything connected as a webcam)
- USB cables for all that ^

I'm not going to explain how to plug it all in.

In general, the camera needs to:
- be plugged in via USB
- be turned on
- be pointing at the specimen on the motor turntable
- be oriented _vertically_ (90 degrees clockwise)
- be focused on the subject

And the motor turntable needs to:
- be plugged in to USB via the driver and the Arduino
- have a subject stuck securely on it

### Canon Video Mode

The Canon DSLR needs to:
- have an SD card in it
- be set to video mode
- have the desired video settings configured (e.g. 60fps vs 30fps)

Then run this in a terminal to create and process a 20s video:
```sh
revile video --length 20
```

### Webcam mode

The camera needs to be streaming from a /dev/video device. For a camera connected via USB with a preview mode available, you can do this using v4l2loopback.
Find the instructions for installing that, then:
```sh
modprobe v4l2loopback
sudo find /dev -name 'video*' | sort | tail -n 1  # to find the device
gphoto2 --stdout --capture-movie | ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -threads 8 -r 60 -f v4l2 /dev/video[DEVICE NUMBER HERE]
```

Once that's working (good luck), run this in a terminal to create and process 500 frames:
```sh
revile stream --frames 500 --stream-port [DEVICE NUMBER HERE]
```

## Note
I have not tested this in this form. Enjoy.
