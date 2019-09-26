import os
import time

import gphoto2 as gp


class GenericCamera:
    def __init__(self, output_dir):
        self.context = gp.Context()
        self.camera = gp.Camera()
        self.output_dir = output_dir


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
        if isinstance(choice_id, str):
            gp.gp_widget_set_value_text(widget, choice_id)
        else:
            try:
                # for i, x in enumerate(widget.get_choices()):
                #     print(f'{i}. {x}')
                choice = widget.get_choice(choice_id)
            except gp.GPhoto2Error:
                choice = choice_id
            widget.set_value(choice)
        self.camera.set_single_config(config_name, widget)

    def wait_for_file(self, timeout=3):
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
                target_path = os.path.join(self.output_dir, event_data.name)
                cam_file.save(target_path)
                self.camera.file_delete(event_data.folder, event_data.name)
                return target_path
        raise FileNotFoundError(f'No new files could be found in {timeout}s.')

    def autofocus(self):
        pass


class CanonCamera(GenericCamera):
    def video(self, length):
        '''
        Capture a video.
        :param length: the length of the video to capture
        :return: the path to the downloaded file or None
        '''
        self._set_config('capturetarget', 1)
        time.sleep(1)  # safety buffer to make sure the motor has started turning

        self._set_config('movierecordtarget', 0)
        print('Recording...')
        time.sleep(length + 2)
        self._set_config('movierecordtarget', 1)
        print('Finished.')
        return self.wait_for_file(10)

    def autofocus(self):
        self._set_config('viewfinder', 1)
        is_focused = False
        loopout = 200
        loop_count = 0
        while not is_focused and loop_count < loopout:
            self._set_config('autofocusdrive', 1)
            event_type, event_data = self.camera.wait_for_event(1000, self.context)
            loop_count += 1
            is_focused = event_data == 'Button 1'  # this is probably wrong but works... ish
        if not is_focused:
            raise Exception('Could not focus!')
        self._set_config('viewfinder', 0)


class NikonCamera(GenericCamera):
    def video(self, length):
        '''
        Capture a video.
        :param length: the length of the video to capture
        :return: the path to the downloaded file or None
        '''
        self._set_config('capturetarget', 1)
        time.sleep(1)  # safety buffer to make sure the motor has started turning
        self._set_config('movie', 1)
        time.sleep(length)
        self._set_config('movie', 0)
        return self.wait_for_file(10)

