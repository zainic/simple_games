import numpy as np
import cv2
import os, sys
from pynput import keyboard

from object import *
from function import *

global pressed_keys

pressed_keys = set()

def on_pressed(key):
    pressed_keys.add(key)

def on_released(key):
    pressed_keys.remove(key)

def main():
    background = Background()
    ship = Ship()
    enemy = Enemy()
    
    listener = keyboard.Listener(on_press=on_pressed, on_release=on_released)
    listener.start()
    
    EXIT = False
    
    while not EXIT:
        try:
            frame = create_frame(background, ship, enemy)
        except:
            ship.move_ship(np.negative(direction))
            frame = create_frame(background, ship, enemy)
            
        cv2.imshow("WarShip Game", frame)
        key = cv2.waitKey(50) & 0xff
        
        direction = get_direction_from_keys(pressed_keys)
        
        ship.move_ship(direction)
        background.move_background(5)
        
        EXIT = get_exit_status(key)
        
    listener.stop()

if __name__ == "__main__":
    main()