# !/usr/bin/python
"""
Create color and depth (black/white) videos from oni file.
First frame from color video is ommited
.
"""
import ctypes
import sys
from time import process_time

import cv2
import numpy as np
from openni import openni2
from openni import _openni2 as c_api
from tqdm import tqdm


def oni_converter(file_path):
    ''' Convert oni file to color and depth avi files.
        avi files will be saved in working directory
        as color.avi and depth.avi

        Parameters
        ----------
        file_path : str
            full path to oni file

    '''
    count = 0
    result = None

    PATH_TO_OPENNI2_SO_FILE = './OpenNI-Linux-x64-2.2/Redist'

    t1_start = process_time()
    openni2.initialize(PATH_TO_OPENNI2_SO_FILE)
    dev = openni2.Device.open_file(file_path.encode('utf-8'))
    c_stream, d_stream = dev.create_color_stream(), dev.create_depth_stream()
    openni2.PlaybackSupport(dev).set_speed(ctypes.c_float(0.0))
    d_stream.start()
    c_stream.start()

    c_images, d_images = [], []
    n_c_frames = openni2.PlaybackSupport(
        dev).get_number_of_frames(c_stream) - 1
    n_d_frames = openni2.PlaybackSupport(dev).get_number_of_frames(d_stream)
    if n_c_frames != n_d_frames:
        print('Разное количество кадров в color и depth потоках!\n'
              f'color - {n_c_frames},  depth - {n_d_frames}')
        sys.exit()

    for i in tqdm(range(n_c_frames)):

        # process depth stream
        d_frame = np.fromstring(d_stream.read_frame().get_buffer_as_uint16(),
                                dtype=np.uint16).reshape(480, 640)
        # Correct the range. Depth images are 12bits
        d_img = np.uint8(d_frame.astype(float) * 255 / 2**12 - 1)
        d_img = cv2.cvtColor(d_img, cv2.COLOR_GRAY2RGB)
        d_img = 255 - d_img
        d_images.append(d_img)
        if i == 0:
            continue
        # process color stream
        c_frame = c_stream.read_frame()
        c_frame_data = c_frame.get_buffer_as_uint8()
        c_img_bgr = np.frombuffer(c_frame_data, dtype=np.uint8)
        c_img_bgr.shape = (480, 640, 3)
        c_img_rgb = cv2.cvtColor(c_img_bgr, cv2.COLOR_BGR2RGB)
        c_images.append(c_img_rgb)
        count += 1
        # yield count
    openni2.unload()

    c_out = cv2.VideoWriter(
        'color.avi', cv2.VideoWriter_fourcc(*'DIVX'), 30, (640, 480))  # надо добавить fps как переменную
    d_out = cv2.VideoWriter(
        'depth.avi', cv2.VideoWriter_fourcc(*'DIVX'), 30, (640, 480))  # надо добавить fps как переменную

    for i in tqdm(range(len(c_images))):
        c_out.write(c_images[i])
        d_out.write(d_images[i])
        count += 1
        # yield count
    c_out.release()
    d_out.release()

    t1_stop = process_time()
    print(f"Process duration, seconds:, {round(t1_stop-t1_start, 3)}")
    return "ONI file has been processed successfully."
    # return()
