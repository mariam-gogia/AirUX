#!/usr/bin/env python

import time
from serial_reader import SerialReader
import pyautogui
import sys
import numpy as np 
import csv

import joblib

from process_signal import Signal_preprocessing

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
	prev_measurements = dict()
	
	# features 6 from sensor 6 data inference
	columns = ['id', 
				'r', 'theta', 'phi', # angles
				'acc_x', 'acc_y', 'acc_z', 'abs_a', # accelerometer
				'g_x', 'g_y', 'g_z', 'abs_g', # gyroscope
				'delta_r', 'delta_theta', 'delta_phi', # angles change
				'delta_acc_x', 'delta_acc_y', 'delta_acc_z', 'delta_abs_acc', # accelerometer change
				'delta_g_x', 'delta_g_y', 'delta_g_z', 'delta_abs_g',# gyroscope change
				'label']

	with open('data.csv', 'w') as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=columns)
		writer.writeheader()

	counter = 0
	recording = False
	list_acc_x, list_acc_y, list_acc_z = [], [], []

	while True:
		counter += 1
		measurements = next(r.read_data())
		move = None

		angles = measurements['angles']
		acc = measurements['accelerations']
		gyro = measurements['gyroscope']

		trigger = None
		trigger_treshold = None

		if recording and len(list_acc_x) < 4:
			list_acc_x.append(acc['a_x'])
			list_acc_y.append(acc['a_x'])
			list_acc_z.append(acc['a_z'])

		if trigger > trigger_treshold and not recording:
			list_acc_x.append(acc['a_x'])
			list_acc_y.append(acc['a_y'])
			list_acc_z.append(acc['a_z'])

		if recording and len(list_acc_x) == 4:
			signal = Signal_preprocessing(list_acc_x, list_acc_y, list_acc_z)
			clean_data = signal.extract_clean_signal()
			model = joblib.load('rf_model.sav')
			action = model.predict(clean_data)

			list_acc_x, list_acc_y, list_acc_z = [], [], []

			print(action)
			
		# # 1200 or some thresh that is not hit by move
		# if acc['abs_a'] > 1250:
		# 	# handle clicks


		# 	# Clicks
		# 	if acc['a_x'] < -10:
		# 		if len(actions) != 0:
		# 			if actions[-1] != 'lc':
		# 				pyautogui.click()
		# 				actions.append('lc')
		# 				move = 'left click'
		# 				print('left click')
		# 		else:
		# 			pyautogui.click()
		# 			actions.append('lc')
		# 			move = 'left click'
		# 			print('left click')

		# 	elif acc['a_x'] > 10:
		# 		if len(actions) != 0:
		# 			if actions[-1] != 'rc':
		# 				pyautogui.click(button='right')
		# 				actions.append('rc')
		# 				move = 'right click'
		# 				print('right click')
		# 		else: 
		# 			pyautogui.click(button='right')
		# 			actions.append('rc')
		# 			move = 'right click'
		# 			print('right click')
		# else:
		# 	# handle moves

		# 	# Moves
		# 	if angles['theta'] > THETA_TRESHOLD and acc['a_x'] < -ACC_TRESHOLD:	
		# 		pyautogui.moveRel(-10,0)
		# 		actions.append('ml')
		# 		move = 'move left'	
		# 		print('move left')

		# 	elif angles['theta'] > THETA_TRESHOLD and acc['a_x'] > ACC_TRESHOLD:
		# 		pyautogui.moveRel(10,0)
		# 		actions.append('mr')
		# 		move = 'move right'
		# 		print('move right')

		# 	elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] < -ACC_TRESHOLD: 
		# 		pyautogui.moveRel(0,-10)
		# 		actions.append('md')
		# 		move = 'move up'
		# 		print('move up')

		# 	elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] > ACC_TRESHOLD:
		# 		pyautogui.moveRel(0, 10)
		# 		actions.append('md')
		# 		move = 'move down'
		# 		print('move down')

		# Scroll
		#if acc['a_y'] < -SCROLL_TRESHOLD:ls
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

		#for key in measurements:
		#	print(measurements[key])
		#print('\n')
		
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


if __name__ == '__main__':
	main()
