import numpy as np
import cv2
import os, sys

from object import *
from function import *

def main():
    background = Background()
    ship = Ship()
    enemy = Enemy()
    
    EXIT = False
    
    while not EXIT:
        try:
            frame = create_frame(background, ship, enemy)
        except:
            ship.move_ship(np.negative(direction))
            frame = create_frame(background, ship, enemy)
            
        cv2.imshow("WarShip Game", frame)
        key = cv2.waitKey(50) & 0xff
        
        direction = get_direction_from_key(key)
        
        ship.move_ship(direction)
        background.move_background(5)
        
        EXIT = get_exit_status(key)
        

if __name__ == "__main__":
    main()