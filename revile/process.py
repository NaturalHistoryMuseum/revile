import math
import os
from datetime import datetime as dt
from queue import Queue
from threading import Thread

import cv2
import numpy as np
from scipy import ndimage
from skimage import feature


class StreamReader(Thread):
    '''
    Reads a stream in another thread and adds the frames to a queue.
    '''

    def __init__(self, video_stream, frame_queue, frame_limit=None, **kwargs):
        '''
        :param video_stream: the Stream object to read from
        :param frame_queue: the queue to put the frames on
        :param frame_limit: the maximum number of frames to read from the stream. Default: None (no
                            limit)
        :param kwargs: Thread init kwargs
        '''
        super().__init__(**kwargs)
        self.video_stream = video_stream
        self.frame_queue = frame_queue
        self.frame_limit = frame_limit if frame_limit is not None else math.inf
        self.frame_count = 0
        self._stopped = False

    def stop(self):
        '''
        Stop the reader from processing frames. This will put a sentinel onto the frame queue before
        ending the thread to ensure consumers are stopped too.
        '''
        self._stopped = True

    def run(self):
        '''
        Reads all frames available (if a file) or up to the frame limit (if a stream) and adds each
        frame to the frame queue.
        '''
        try:
            with self.video_stream as stream:
                while self.frame_count < self.frame_limit and not self._stopped:
                    reading, frame = stream.read()
                    if not reading:
                        if self.video_stream.is_file:
                            break
                        else:
                            continue
                    else:
                        self.frame_count += 1
                        self.frame_queue.put((self.frame_count, frame))
        finally:
            # always dump a sentinel onto the queue to indicate to consumers that we're done reading
            self.frame_queue.put(None)


class StreamProcessor(Thread):
    '''
    Processes frames from a queue by extracting the middle column of pixels and concatenating them
    together into an image.
    '''

    def __init__(self, frame_queue, **kwargs):
        '''
        :param frame_queue: the queue to get the frames from
        :param kwargs: Thread init kwargs
        '''
        super().__init__(**kwargs)
        self.frame_queue = frame_queue
        self.image = None
        self.done = False
        self.count = 0

    def run(self):
        '''
        Consumes frames from the frame queue, extracts the midline from each and adds it to the
        image.
        '''
        for frame_number, frame in iter(self.frame_queue.get, None):
            h, w, pix = frame.shape
            midline = frame[h // 2, :, :].reshape((1, w, pix))
            if self.image is None:
                self.image = midline
            else:
                self.image = np.concatenate([self.image, midline], axis=0)
            self.count = frame_number
        self.done = True


class Stream:
    def __init__(self, port_or_file, output_dir):
        '''
        An opencv video stream.
        :param port_or_file: int if port, str file path if file
        '''
        self.port_or_file = port_or_file
        self.is_file = not isinstance(port_or_file, int)
        self._start = None
        self._elapsed = None
        self.output_dir = output_dir
        self.fn = str(int(dt.timestamp(dt.now()))) + '.png'

    def __enter__(self):
        self._start = dt.now()
        self._stream = cv2.VideoCapture(self.port_or_file)
        return self._stream

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._elapsed = (dt.now() - self._start).total_seconds()
        self._stream.release()
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

    def process(self, frame_count=None, display_fps=30, max_frame_queue_size=100):
        '''
        Process the stream.

        :param frame_count: only needed for port - number of frames to process before terminating
        :param display_fps: the fps to display the output image at during processing, the higher
                            this value is, the more it will impact overall processing perforamance.
                            Default: 30.
        :param max_frame_queue_size: the maximum size of the frame queue, this is directly related
                                     to memory usage. Default: 100.
        :return: path to processed image file
        '''
        if not self.is_file and frame_count is None:
            raise ValueError(
                'This will stream forever, which is probably a bad idea. Set a frame limit.')

        frame_queue = Queue(maxsize=max_frame_queue_size)
        reader = StreamReader(self, frame_queue, frame_count)
        processor = StreamProcessor(frame_queue)
        reader.start()
        processor.start()

        wait_time = 1000 // display_fps

        try:
            while not processor.done:
                if processor.image is not None:
                    cv2.imshow('Scan output', processor.image)
                    k = cv2.waitKey(wait_time) & 0xff
                    if k == 27:
                        reader.stop()
                        break
        finally:
            cv2.destroyAllWindows()

        # make sure both threads have finished
        reader.join()
        processor.join()

        print(f'Processed in {self._elapsed} seconds '
              f'({round(reader.frame_count / self._elapsed, 1)} fps)')
        image = ndimage.rotate(processor.image, 270)
        target_path = str(int(dt.timestamp(dt.now()))) + '.png'
        cv2.imwrite(target_path, image)
        self.image = image
        return target_path

    def crop(self, output_dir):
        b = 10
        template = self.image[b:-b, :b, :]

        img = self.image[b:-b, b:, :]
        result = feature.match_template(img, template)
        result = result[..., 0]
        ij = np.unravel_index(np.argmax(result), result.shape)
        x, y = ij[::-1]

        whole_img = self.image[:, :x + b, :]
        target_path = os.path.join(output_dir, self.fn)
        cv2.imwrite(target_path, whole_img)
        return target_path
