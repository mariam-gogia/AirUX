#!/usr/bin/env python

from serial_reader import SerialReader
import pyautogui
import sys
import numpy as np 

pyautogui.FAILSAFE = True

# Global Variables
THETA_TRESHOLD = 25
ACC_TRESHOLD = 300
RIGHT_CLICK_TRESHOLD = 850
LEFT_CLICK_TRESHOLD = -550
SCROLL_TRESHOLD = 600

if len(sys.argv) != 2:
    print ("Unmatch number of arguments should be 2, given", len(sys.argv))
    print ("Please use format: python SensorTile_Animation_args.py SerialAddress")
	
def main():
	r = SerialReader(port=sys.argv[1])
	r.initialize_connection()

	while True:
		measurements = next(r.read_data())

		angles = measurements['angles']
		acc = measurements['accelerations']

		# Moves
		if angles['theta'] > THETA_TRESHOLD and acc['a_x'] < -ACC_TRESHOLD:	
			pyautogui.moveRel(-20,0)	
			print('move left')

		elif angles['theta'] > THETA_TRESHOLD and acc['a_x'] > ACC_TRESHOLD:
			pyautogui.moveRel(20,0)
			print('move right')

		elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] < -ACC_TRESHOLD: 
			pyautogui.moveRel(0,-20)
			print('move up')

		elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] > ACC_TRESHOLD:
			pyautogui.moveRel(0, 20)
			print('move down')

		
		# Clicks
		if acc['a_x'] < LEFT_CLICK_TRESHOLD:
			pyautogui.click()
			print('left click')

		elif acc['a_x'] > RIGHT_CLICK_TRESHOLD:
			pyautogui.click(button='right')
			print('right click')

		# Scroll
		if acc['a_y'] < -SCROLL_TRESHOLD:
			pyautogui.scroll(50)
			print('scroll down')

		elif acc['a_y'] > SCROLL_TRESHOLD:
			pyautogui.scroll(-50)
			print('scroll up')

		print(measurements)
		print('\n')

if __name__ == '__main__':
	main()
