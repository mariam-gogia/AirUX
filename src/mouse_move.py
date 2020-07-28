#!/usr/bin/env python
from serial_reader import SerialReader
import pyautogui
import sys
import numpy as np 
pyautogui.FAILSAFE = True


def main():
	

	r = SerialReader(port='/dev/cu.usbmodemFFFFFFFEFFFF1')
	r.initialize_connection()

	while True:
		measurements = next(r.read_data())

		angles = measurements['angles']
		acc = measurements['accelerations']

		if angles['theta'] > 25 and acc['a_x'] < -350:	
			pyautogui.moveRel(-20,0)	
			print('move left')

		elif angles['theta'] > 25 and acc['a_x'] > 350:
			pyautogui.moveRel(20,0)
			print('move right')

		elif angles['theta'] > 25 and acc['a_y'] < -350: 
			pyautogui.moveRel(0,-20)
			print('move up')

		elif angles['theta'] > 25 and acc['a_y'] > 350:
			pyautogui.moveRel(0, 20)
			print('move down')

		

		print(measurements)
		print('\n')

if __name__ == '__main__':
	main()
