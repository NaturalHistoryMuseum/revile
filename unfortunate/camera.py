import os
import time

import gphoto2 as gp


class CanonCamera:
    def __init__(self):
        self.context = gp.Context()
        self.camera = gp.Camera()

    def __enter__(self):
        self.camera.init(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.camera.exit(self.context)

    def _set_config(self, config_name, choice_id):
        '''
        Set a config option on the camera.
        :param config_name: the name of the config option
        :param choice_id: the id of the value (use widget.get_choices() to see the options) to set
        '''
        widget = self.camera.get_single_config(config_name)
        choice = widget.get_choice(choice_id)
        widget.set_value(choice)
        self.camera.set_single_config(config_name, widget)

    def _wait_for_file(self, timeout=3):
        '''
        Wait for a "new file" event, then download the new file.
        :param timeout: the amount of time (in seconds) to wait for the event before failing
        :return: the path to the downloaded file or None
        '''
        loop_count = 0
        event_type = 0
        loop_time = 100  # milliseconds
        loopout = (timeout * 1000) / loop_time
        while event_type != gp.GP_EVENT_FILE_ADDED and loop_count < loopout:
            event_type, event_data = self.camera.wait_for_event(loop_time, self.context)
            if event_type == gp.GP_EVENT_FILE_ADDED:
                cam_file = self.camera.file_get(
                    event_data.folder, event_data.name, gp.GP_FILE_TYPE_NORMAL)
                target_path = os.path.join(os.getcwd(), event_data.name)
                cam_file.save(target_path)
                return target_path
        raise FileNotFoundError(f'No new files could be found in {timeout}s.')

    def video(self, length):
        '''
        Capture a video.
        :param length: the length of the video to capture
        :return: the path to the downloaded file or None
        '''
        self._set_config('capturetarget', 1)
        time.sleep(1)  # safety buffer to make sure the motor has started turning
        self._set_config('movierecordtarget', 0)
        time.sleep(length)
        self._set_config('movierecordtarget', 1)
        return self._wait_for_file(10)
