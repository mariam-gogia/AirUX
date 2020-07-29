#!/usr/bin/env python

from serial_reader import SerialReader
import pyautogui
import sys
import numpy as np 

pyautogui.FAILSAFE = True

# Global Variables
THETA_TRESHOLD = 25
ACC_TRESHOLD = 300
RIGHT_CLICK_TRESHOLD = 350
LEFT_CLICK_TRESHOLD = -350
SCROLL_TRESHOLD = 600
SWIPE_TRESHOLD = 1000

# if len(sys.argv) != 2:
#     print ("Unmatch number of arguments should be 2, given", len(sys.argv))

def main():
	r = SerialReader(port='/dev/cu.usbmodemFFFFFFFEFFFF1')
	r.initialize_connection()

	actions = []

	while True:
		measurements = next(r.read_data())

		angles = measurements['angles']
		acc = measurements['accelerations']

		# 1200 or some thresh that is not hit by move
		if acc['abs_A'] > 1250:
			# handle clicks
			# Clicks
			if acc['a_x'] < -10:
				if actions[-1] != 'lc':
					pyautogui.click()
					actions.append('lc')
					print('left click')

			elif acc['a_x'] > 10:
				if actions[-1] != 'rc':
					pyautogui.click(button='right')
					actions.append('rc')
					print('right click')
		else:
			# handle moves

			# Moves
			if angles['theta'] > THETA_TRESHOLD and acc['a_x'] < -ACC_TRESHOLD:	
				pyautogui.moveRel(-20,0)
				actions.append('ml')	
				print('move left')

			elif angles['theta'] > THETA_TRESHOLD and acc['a_x'] > ACC_TRESHOLD:
				pyautogui.moveRel(20,0)
				actions.append('mr')
				print('move right')

			elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] < -ACC_TRESHOLD: 
				pyautogui.moveRel(0,-20)
				actions.append('md')
				print('move up')

			elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] > ACC_TRESHOLD:
				pyautogui.moveRel(0, 20)
				actions.append('md')
				print('move down')

		# Scroll
		#if acc['a_y'] < -SCROLL_TRESHOLD:
		#	pyautogui.scroll(50)
		#	print('scroll down')

		#elif acc['a_y'] > SCROLL_TRESHOLD:
		#	pyautogui.scroll(-50)
		#	print('scroll up')

		# Swipe
		#if acc['a_x'] < -SWIPE_TRESHOLD:
		#	pyautogui.keyDown('ctrl')
		#	pyautogui.press('left')
		#	pyautogui.keyUp('ctrl')

		#elif acc['a_x'] > SWIPE_TRESHOLD:
		#	pyautogui.keyDown('ctrl')
		#	pyautogui.press('right')
		#	pyautogui.keyUp('ctrl')

		#print(measurements)
		#print('\n')

if __name__ == '__main__':
	main()
