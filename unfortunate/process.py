from datetime import datetime as dt

import cv2
import numpy as np
from scipy import ndimage


class Stream:
    def __init__(self, port_or_file):
        '''
        An opencv video stream.
        :param port_or_file: int if port, str file path if file
        '''
        self.port_or_file = port_or_file
        self._is_file = not isinstance(port_or_file, int)
        self._start = None
        self._elapsed = None

    def __enter__(self):
        self._start = dt.now()
        self._stream = cv2.VideoCapture(self.port_or_file)
        return self._stream

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._elapsed = (dt.now() - self._start).total_seconds()
        self._stream.release()
        cv2.destroyAllWindows()
        self._start = None

    @property
    def framerate(self):
        '''
        Get an estimate of the stream's current framerate.
        :return: the current framerate
        '''
        with self as stream:
            for i in range(100):
                reading, frame = stream.read()
        return 100 / self._elapsed

    @staticmethod
    def _get_midline(image, frame):
        '''
        Add the middle line of pixels to the current image.
        :param image: the image produced from previous frames
        :param frame: the current frame
        :return: the image array with the new line of pixels added
        '''
        h, w, pix = frame.shape
        midline = frame[h // 2, :, :].reshape((1, w, pix))
        if image is None:
            image = midline
        else:
            image = np.concatenate([image, midline], axis=0)
        return image

    def process(self, frame_count=None):
        '''
        Process the stream.
        :param frame_count: only needed for port - number of frames to process before terminating
        :return: path to processed image file
        '''
        if not self._is_file and frame_count is None:
            raise ValueError(
                'This will stream forever, which is probably a bad idea. Set a frame limit.')
        c = 0
        image = None
        with self as stream:
            while (c < frame_count) if frame_count is not None else True:
                try:
                    reading, frame = stream.read()
                    if not reading:
                        if self._is_file:
                            break
                        else:
                            continue
                    image = self._get_midline(image, frame)
                    c += 1
                    cv2.imshow('video output', image)
                    k = cv2.waitKey(10) & 0xff
                    if k == 27:
                        break
                except KeyboardInterrupt:
                    break
        print(f'Processed in {self._elapsed} seconds ({round(c / self._elapsed, 1)} fps)')
        image = ndimage.rotate(image, 270)
        target_path = str(int(dt.timestamp(dt.now()))) + '.png'
        cv2.imwrite(target_path, image)
        return target_path
