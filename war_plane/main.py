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
    
    delay_shoot = 10
    
    while not EXIT:
        delay_shoot -= 1
        
        try:
            frame = create_frame(background, ship, enemy)
        except:
            ship.move_ship(np.negative(direction))
            frame = create_frame(background, ship, enemy)
            
        cv2.imshow("WarShip Game", frame)
        key = cv2.waitKey(10) & 0xff
        
        direction = get_direction_from_keys(pressed_keys)
        
        if is_shooting(pressed_keys) and delay_shoot <= 0:
            ship.shoot_bullet()
            delay_shoot = 10
        
        ship.move_ship(direction)
        background.move_background(3)
        
        EXIT = get_exit_status(key)
        
    listener.stop()

if __name__ == "__main__":
    main()