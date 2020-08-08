#!/usr/bin/env python
import argparse
import time
from serial_reader import SerialReader
import sys
import numpy as np
import csv

# Global Variables
THETA_TRESHOLD = 25
ACC_TRESHOLD = 300
RIGHT_CLICK_TRESHOLD = 350
LEFT_CLICK_TRESHOLD = -350
SCROLL_TRESHOLD = 600
SWIPE_TRESHOLD = 1000

# features
DATA_COLUMNS = [
    'id',
    'r', 'theta', 'phi',  # angles
    'acc_x', 'acc_y', 'acc_z',  # 'abs_a',  # accelerometer
    'g_x', 'g_y', 'g_z', 'abs_g',  # gyroscope
    # 'delta_r', 'delta_theta', 'delta_phi',  # angles change
    # 'delta_acc_x', 'delta_acc_y', 'delta_acc_z', 'delta_abs_acc',  # accelerometer change
    # 'delta_g_x', 'delta_g_y', 'delta_g_z', 'delta_abs_g',  # gyroscope change
    'label'
]

parser = argparse.ArgumentParser(description='Record motion gesture training data.')
parser.add_argument('--label', type=str, help='Label for the data being recorded.')
parser.add_argument('--port', default='/dev/cu.usbmodemFFFFFFFEFFFF1', type=str, help='SensorTile port.')

args = parser.parse_args()


def record_data(reader, counter, label, columns=DATA_COLUMNS):
    data = []

    while len(data) < 4:
        current_measurement = next(reader.read_data())

        angles = current_measurement['angles']
        acc = current_measurement['accelerations']
        gyro = current_measurement['gyroscope']

        # init values
        # delta_r, delta_theta, delta_phi = 0, 0, 0
        # delta_acc_x, delta_acc_y, delta_acc_z, delta_abs_acc = 0, 0, 0, 0
        # delta_g_x, delta_g_y, delta_g_z, delta_abs_g = 0, 0, 0, 0

        datum = {
            'id': counter,
            'r': angles['r'],
            'theta': angles['theta'],
            'phi': angles['phi'],
            'acc_x': acc["a_x"],
            'acc_y': acc["a_y"],
            'acc_z': acc["a_z"],
            'g_x': gyro["g_x"],
            'g_y': gyro["g_y"],
            'g_z': gyro["g_z"],
            'abs_g': gyro["abs_g"],
            'label': label
        }

        data.append(datum)
        time.sleep(0.01)


    with open('%s.csv' % label, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)

        for datum in data:
            writer.writerow(datum)


def main():
    r = SerialReader(port='/dev/cu.usbmodemFFFFFFFEFFFF1')
    r.initialize_connection()

    num_data_points = 100
    cur_i = 0

    time.sleep(2)

    while cur_i < num_data_points:
        print('3 seconds')
        time.sleep(1)
        print('2 seconds')
        time.sleep(1)
        print('1 second')
        time.sleep(1)

        print('go!')

        record_data(reader=r, counter=cur_i, label=args.label)

        print('Recorded. Sleeping for 5 seconds..')

        time.sleep(2)

        cur_i += 1


if __name__ == '__main__':
    main()


def _main():
    r = SerialReader(port='/dev/cu.usbmodemFFFFFFFEFFFF1')
    r.initialize_connection()

    actions = []
    prev_measurements = dict()

    with open('data.csv', 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()

    counter = 0

    while True:
        counter += 1
        measurements = next(r.read_data())
        angles = measurements['angles']
        acc = measurements['accelerations']
        gyro = measurements['gyroscope']

        delta_r, delta_theta, delta_phi = 0, 0, 0
        delta_acc_x, delta_acc_y, delta_acc_z, delta_abs_acc = 0, 0, 0, 0
        delta_g_x, delta_g_y, delta_g_z, delta_abs_g = 0, 0, 0, 0

        if len(prev_measurements) > 0:
            # angles
            delta_r = angles['r'] - prev_measurements['angles']['r']
            delta_theta = angles['theta'] - prev_measurements['angles']['theta']
            delta_phi = angles['phi'] - prev_measurements['angles']['phi']

            # accelerometer
            delta_acc_x = acc['a_x'] - prev_measurements['accelerations']['a_x']
            delta_acc_y = acc['a_y'] - prev_measurements['accelerations']['a_y']
            delta_acc_z = acc['a_z'] - prev_measurements['accelerations']['a_y']
            delta_abs_acc = acc['abs_a'] - prev_measurements['accelerations']['abs_a']

            # gyroscope
            delta_g_x = gyro['g_x'] - prev_measurements['gyroscope']['g_x']
            delta_g_y = gyro['g_y'] - prev_measurements['gyroscope']['g_y']
            delta_g_z = gyro['g_z'] - prev_measurements['gyroscope']['g_z']
            delta_abs_g = gyro['abs_g'] - prev_measurements['gyroscope']['abs_g']

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

        # for key in measurements:
        #    print(measurements[key])
        # print('\n')

        with open("data.csv", 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)

            info = {
                'id': counter,

                # sensored data
                'r': angles['r'],
                'theta': angles['theta'],
                'phi': angles['phi'],

                'acc_x': acc["a_x"],
                'acc_y': acc["a_y"],
                'acc_z': acc["a_z"],
                'abs_a': acc["abs_a"],

                'g_x': gyro["g_x"],
                'g_y': gyro["g_y"],
                'g_z': gyro["g_z"],
                'abs_g': gyro["abs_g"],

                # inferenced changed data
                'delta_r': delta_r,
                'delta_theta': delta_theta,
                'delta_phi': delta_phi,

                'delta_acc_x': delta_acc_x,
                'delta_acc_y': delta_acc_y,
                'delta_acc_z': delta_acc_z,
                'delta_abs_acc': delta_abs_acc,

                'delta_g_x': delta_g_x,
                'delta_g_y': delta_g_y,
                'delta_g_z': delta_g_z,
                'delta_abs_g': delta_abs_g,

                'label': 0
            }

            # add to csv file
            print(info['id'])
            writer.writerow(info)

        # save to the prev
        prev_measurements = measurements

        # slow-down terminal results printing
        time.sleep(0.01)