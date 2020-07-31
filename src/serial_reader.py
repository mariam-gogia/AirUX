#!/usr/bin/env python
import serial
import sys
import traceback

class SerialReader(object):

	def __init__(self, port, baud_rate=9600, timeout=2):
		self.port = port
		self.baud_rate = baud_rate
		self.timeout = timeout

		self.serial = None

		# flags
		self.data_check = 1

		# storage
		self.current_gyro_measurement = None


	def initialize_connection(self):
		print('Initializing connection to %s, baud_rate=%s' % (self.port, self.baud_rate))

		try:
			self.serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
		except Exception:
			print('Error opening connection.')
			print(traceback.format_exc())
			sys.exit(1)  # TODO: this should not exit, raise and let consumers handle


	def is_ready(self, bytes_expected):
		return self.serial.in_waiting >= bytes_expected

	def read_data(self):
		# if self.data_check:

		measurements = {}

		while True:
			if self.serial.in_waiting > 0:
				line = self.serial.readline()
				line = line.decode('utf-8')

				if 'Flipped' in line:
					measurements['action'] = 'flip'

				if 'theta' in line:
					line = line.strip('\n').strip('\r').split(',')
					angles_measurements = {
						'r': float(line[0].split(' ')[-1]),
						'theta': float(line[1].split(' ')[-1]),
						'phi': float(line[2].split(' ')[-1]),
					}
					measurements['angles'] = angles_measurements

				if 'A_x' in line and 'A_y' in line and 'A_z' in line:
					line = line.strip('\n').strip('\r').split(',')
					acc_measurements = {
						'a_x': float(line[0].split(' ')[-1]),
						'a_y': float(line[1].split(' ')[-1]),
						'a_z': float(line[2].split(' ')[-1]),
						'abs_a': float(line[3].split(' ')[-1])
					}

					measurements['accelerations'] = acc_measurements

				if 'GYR_X' in line and 'GYR_Y' in line and 'GYR_Z' in line:
					line = line.strip('\n').strip('\r').split(',')
					gyro_measurements = {
						'g_x': float(line[0].split(' ')[-1]),
						'g_y': float(line[1].split(' ')[-1]),
						'g_z': float(line[2].split(' ')[-1]),
						'abs_g': float(line[3].split(' ')[-1])
					}

					measurements['gyroscope'] = gyro_measurements

				if 'angles' in measurements and 'accelerations' in measurements:
					if 'gyroscope' in measurements:
						yield measurements
						measurements = {}

				if 'action' in measurements:
					yield measurements
					measurements = {}
					


def main():
	reader = SerialReader(port='/dev/cu.usbmodemFFFFFFFEFFFF1')
	reader.initialize_connection()
	reader.read_data()


if __name__ == '__main__':
	main()
