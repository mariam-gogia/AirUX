#!/usr/bin/env python
import joblib
import numpy as np 
import pyautogui
import sys
import traceback

from datetime import datetime, timedelta

from process_signal import SignalPreprocessing
from serial_reader import SerialReader

# Global Variables
ACC_TRESHOLD = 300
GESTURE_STARTED_THRESH = 2000
THETA_TRESHOLD = 25

BACK_IN_TIME_TICKS = 4

MODEL_FILEPATH = 'rf_model.sav'
SENSOR_TILE_PORT = '/dev/cu.usbmodemFFFFFFFEFFFF1'

# config
pyautogui.FAILSAFE = True

class MouseMove(object):

    def __init__(self, port=SENSOR_TILE_PORT):
        self.port = port

        self.last_flip_dt = None

        self.mouse_positions = [None for x in range(10)]
        self.current_mouse_pos_idx = 0

        self.last_measurements = dict()
        self.measurements_counter = 0
        self.listening_for_gesture = False
        self.list_acc_x, self.list_acc_y, self.list_acc_z = [], [], []

        self.model = joblib.load(MODEL_FILEPATH)

        try:
            self.r = SerialReader(self.port)
            self.r.initialize_connection()
        except Exception as e:
            print('Error initializing serial connection to sensor tile. Error: %s' % str(e))
            print('Stacktrace:')
            print(traceback.format_exc())


    def calculate_before_flip_mouse_position(self):
        return self.mouse_positions[self.current_mouse_pos_idx - BACK_IN_TIME_TICKS]


    def handle_action(self, action):
        if action == 'flip':
            pre_click_mouse_pos = self.calculate_before_flip_mouse_position()
            pyautogui.moveTo(pre_click_mouse_pos.x, pre_click_mouse_pos.y)

            if self.last_flip_dt is None:
                pyautogui.click()
                self.last_flip_dt = datetime.now()
            else:
                if datetime.now() - self.last_flip_dt > timedelta(seconds=1):
                    pyautogui.click()
                    self.last_flip_dt = datetime.now()


    def handle_mouse_move(self, angles, acc):
        """
        Output relative mouse move position based on angles and accelerations.
        """
        if angles['theta'] > THETA_TRESHOLD and acc['a_x'] < -ACC_TRESHOLD:
            print('move left')
            pyautogui.moveRel(-10, 0)

        elif angles['theta'] > THETA_TRESHOLD and acc['a_x'] > ACC_TRESHOLD:
            print('move right')
            pyautogui.moveRel(10, 0)

        elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] < -ACC_TRESHOLD: 
            print('move up')
            pyautogui.moveRel(0, -10)

        elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] > 200:
            print('move down')
            pyautogui.moveRel(0, 10)


    def update_last_measurements(self, acc, angles, gyro, measurements):
        if len(self.last_measurements) > 0:
            delta_r, delta_theta, delta_phi = 0, 0, 0 
            delta_acc_x, delta_acc_y, delta_acc_z, delta_abs_acc = 0, 0, 0, 0
            delta_g_x, delta_g_y, delta_g_z, delta_abs_g = 0, 0, 0, 0

            # angles
            delta_r = angles['r'] - self.last_measurements['angles']['r']
            delta_theta = angles['theta'] - self.last_measurements['angles']['theta']
            delta_phi = angles['phi'] - self.last_measurements['angles']['phi']

            # accelerometer 
            delta_acc_x = acc['a_x'] - self.last_measurements['accelerations']['a_x']
            delta_acc_y = acc['a_y'] - self.last_measurements['accelerations']['a_y']
            delta_acc_z = acc['a_z'] - self.last_measurements['accelerations']['a_y']
            delta_abs_acc = acc['abs_a'] - self.last_measurements['accelerations']['abs_a']

            # gyroscope 
            delta_g_x = gyro['g_x'] - self.last_measurements['gyroscope']['g_x']
            delta_g_y = gyro['g_y'] - self.last_measurements['gyroscope']['g_y']
            delta_g_z = gyro['g_z'] - self.last_measurements['gyroscope']['g_z']
            delta_abs_g = gyro['abs_g'] - self.last_measurements['gyroscope']['abs_g']

            measurements['delta_r'], measurements['delta_theta'], measurements['delta_phi'] = \
                str(round(delta_r, 2)), str(round(delta_theta, 2)), str(round(delta_phi, 2))
            measurements['delta_acc_x'], measurements['delta_acc_y'], measurements['delta_acc_z'], measurements['delta_abs_acc']= \
                str(round(delta_acc_x, 2)), str(round(delta_acc_y, 2)), str(round(delta_acc_z, 2)), str(round(delta_abs_acc, 2))
            measurements['delta_g_x'], measurements['delta_g_y'], measurements['delta_g_z'], measurements['delta_abs_g'] = \
                str(round(delta_g_x, 2)), str(round(delta_g_y, 2)), str(round(delta_g_z, 2)), str(round(delta_abs_g, 2))
        else:
            measurements['delta_r'], measurements['delta_theta'], measurements['delta_phi'] = 0, 0, 0
            measurements['delta_acc_x'], measurements['delta_acc_y'], measurements['delta_acc_z'], measurements['delta_abs_acc'] = 0, 0, 0, 0
            measurements['delta_g_x'], measurements['delta_g_y'], measurements['delta_g_z'], measurements['delta_abs_g'] = 0, 0, 0, 0

        self.last_measurements = measurements


    def do_the_swipe(self, swipe_direction):
        assert type(swipe_direction) == str, 'swipe_direction is not a string.'

        pyautogui.keyDown('ctrl')
        pyautogui.press(swipe_direction)
        pyautogui.keyUp('ctrl')


    def reset_internal_state(self):
        self.listening_for_gesture = False
        self.list_acc_x, self.list_acc_y, self.list_acc_z = [], [], []


    def run(self):
        while True:
            measurements = next(self.r.read_data())

            # pyautogui.position() returns <class 'pyautogui.Point'>, e.g. Point(x=1211, y=276)
            self.mouse_positions[self.current_mouse_pos_idx] = pyautogui.position()
            self.current_mouse_pos_idx += 1

            if self.current_mouse_pos_idx >= len(self.mouse_positions):
                self.current_mouse_pos_idx = 0

            if measurements.get('action', False):
                # handling an action
                action = measurements['action']
                self.handle_action(action)
                
            if measurements.get('angles', False) and measurements.get('accelerations', False) and measurements.get('gyroscope', False):
                angles = measurements['angles']
                acc = measurements['accelerations']
                gyro = measurements['gyroscope']

                # we are not listening_for_gesture, r > 2000, i.e. previous measurement marked the
                # start of the gesture. backfill the list_acc_* with previous measurements
                # and also add the current measurement
                if angles['r'] > GESTURE_STARTED_THRESH and not self.listening_for_gesture:
                    self.list_acc_x.append(self.last_measurements['accelerations']['a_x'])
                    self.list_acc_y.append(self.last_measurements['accelerations']['a_y'])
                    # this used to be appending to y also
                    self.list_acc_z.append(self.last_measurements['accelerations']['a_z'])
                    
                    self.list_acc_x.append(acc['a_x'])
                    self.list_acc_y.append(acc['a_y'])
                    self.list_acc_z.append(acc['a_z'])
                    self.listening_for_gesture = True

                # we are listening_for_gesture (listening for gesture measurements) and we have not
                # accumulated the required 4 measurements yet, save them and keep listening_for_gesture
                if self.listening_for_gesture and len(self.list_acc_x) < 4:
                    self.list_acc_x.append(acc['a_x'])
                    self.list_acc_y.append(acc['a_x'])
                    self.list_acc_z.append(acc['a_z'])

                # we are listening_for_gesture (listening for gesture measurements) and we have accumulated
                # the required 4 measurements. Feed these through a model to get the action.
                did_the_action = False
                if self.listening_for_gesture and len(self.list_acc_x) == 4:
                    clean_signal = SignalPreprocessing.extract_clean_signal(self.list_acc_x, self.list_acc_y, self.list_acc_z)
                    action = self.model.predict([clean_signal])

                    print('Received Action: %s' % (action))

                    if action == 1:
                        self.do_the_swipe('right')
                    elif action == 2:
                        self.do_the_swipe('left')
                    else:
                        print('Unknown action.')

                    # action completed, reset
                    self.reset_internal_state()
                    did_the_action = True

                if not self.listening_for_gesture and not did_the_action:
                    # move the mouse if not listening for gesture and this measurement was not a final
                    # one of the four for the gesture.
                    self.handle_mouse_move(angles, acc)

                self.update_last_measurements(acc, angles, gyro, measurements)


def main():
    mouse_move = MouseMove()
    mouse_move.run()


if __name__ == '__main__':
    main()
