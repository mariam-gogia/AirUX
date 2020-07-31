#!/usr/bin/env python
import pyautogui
import sys
import numpy as np 

from datetime import datetime, timedelta

from serial_reader import SerialReader

pyautogui.FAILSAFE = True

# Global Variables
THETA_TRESHOLD = 25
ACC_TRESHOLD = 300
RIGHT_CLICK_TRESHOLD = 350
LEFT_CLICK_TRESHOLD = -350
SCROLL_TRESHOLD = 600
SWIPE_TRESHOLD = 1000

BACK_IN_TIME_TICKS = 4

# if len(sys.argv) != 2:
#     print ("Unmatch number of arguments should be 2, given", len(sys.argv))


def calculate_before_flip_mouse_position(mouse_positions, pos_counter):
    return mouse_positions[pos_counter - BACK_IN_TIME_TICKS]


def main():
    r = SerialReader(port='/dev/cu.usbmodemFFFFFFFEFFFF1')
    r.initialize_connection()

    actions = []
    last_flip_dt = None

    mouse_positions = [None for x in range(10)]
    pos_counter = 0

    while True:
        measurements = next(r.read_data())

        # pyautogui.position() returns <class 'pyautogui.Point'>, e.g. Point(x=1211, y=276)
        mouse_positions[pos_counter] = pyautogui.position()
        pos_counter += 1

        if pos_counter >= len(mouse_positions):
            pos_counter = 0

        if measurements.get('action', False):
            # handling an action
            action = measurements['action']
            if action == 'flip':
                print('action = flip')
                pre_click_mouse_pos = calculate_before_flip_mouse_position(
                    mouse_positions,
                    pos_counter
                )
                pyautogui.moveTo(pre_click_mouse_pos.x, pre_click_mouse_pos.y)

                if last_flip_dt is None:
                    print('last_flip_dt is none')
                    pyautogui.click()
                    last_flip_dt = datetime.now()
                else:
                    print('last_flip_dt is not none')
                    if datetime.now() - last_flip_dt > timedelta(seconds=1):
                        print('last_flip_dt over 1 second ago')
                        # do the flip
                        pyautogui.click()
                        last_flip_dt = datetime.now()

        if measurements.get('angles', False) and measurements.get('accelerations', False):
            angles = measurements['angles']
            acc = measurements['accelerations']

        #   # 1200 or some thresh that is not hit by move
        #   if acc['abs_A'] > 1250:
        #       # handle clicks
        #       # Clicks
        #       if acc['a_x'] < -10:
        #           if actions[-1] != 'lc':
        #               pyautogui.click()
        #               actions.append('lc')
        #               print('left click')

        #       elif acc['a_x'] > 10:
        #           if actions[-1] != 'rc':
        #               pyautogui.click(button='right')
        #               actions.append('rc')
        #               print('right click')
        #   else:
        #       # handle moves

                # Moves
            if angles['theta'] > THETA_TRESHOLD and acc['a_x'] < -ACC_TRESHOLD:
                pyautogui.moveRel(-10,0)
                actions.append('ml')    
                print('move left')


            elif angles['theta'] > THETA_TRESHOLD and acc['a_x'] > ACC_TRESHOLD:
                pyautogui.moveRel(10,0)
                actions.append('mr')
                print('move right')

            elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] < -ACC_TRESHOLD: 
                pyautogui.moveRel(0,-10)
                actions.append('md')
                print('move up')

            elif angles['theta'] > THETA_TRESHOLD and acc['a_y'] > 200:
                pyautogui.moveRel(0, 10)
                actions.append('md')
                print('move down')

        # Scroll
        #if acc['a_y'] < -SCROLL_TRESHOLD:
        #   pyautogui.scroll(50)
        #   print('scroll down')

        #elif acc['a_y'] > SCROLL_TRESHOLD:
        #   pyautogui.scroll(-50)
        #   print('scroll up')

        # Swipe
        #if acc['a_x'] < -SWIPE_TRESHOLD:
        #   pyautogui.keyDown('ctrl')
        #   pyautogui.press('left')
        #   pyautogui.keyUp('ctrl')

        #elif acc['a_x'] > SWIPE_TRESHOLD:
        #   pyautogui.keyDown('ctrl')
        #   pyautogui.press('right')
        #   pyautogui.keyUp('ctrl')

        #print(measurements)
        #print('\n')

if __name__ == '__main__':
    main()
