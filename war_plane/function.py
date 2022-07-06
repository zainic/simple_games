import numpy as np
import cv2
import os, sys

from object import *

def create_frame(background, ship, enemy):
    """
    Create one frame from the condition

    Args:
        background (class Background): background of the game
        ship (class Ship): ship that player control
        enemy (class Enemy): enemy that attack player

    Returns:
        ndarray: image of the current condition
    """
    
    frame = np.copy(background.background)
    
    # Show ship
    position = ship.position
    texture = ship.ship_texture["lv" + str(ship.current_level)]
    part_minus_ship = np.copy(frame[position[0] : position[0] + 64, position[1] : position[1] + 64])
    part_minus_ship[np.where((texture != [0, 0, 0]).all(axis=2))] = [0, 0, 0]
    frame[position[0] : position[0] + 64, position[1] : position[1] + 64] = part_minus_ship + texture
    
    return frame

# def get_input_key():
#     """
#     Allow us to get multiple pressed key

#     Returns:
#         array: list of string that user pressed key
#     """
    
#     listener = Listener(on_press=on_press, on_release=on_release)
#     listener.start()
    
#     return keys

def get_direction_from_key(key):
    """
    function that return direction for ship from key pressed

    Args:
        key (int): key that got from cv2.waitKey()

    Returns:
        array: direction 
    """
    
    if key == ord("w"):
        direction = UP
    elif key == ord("s"):
        direction = DOWN
    elif key == ord("a"):
        direction = LEFT
    elif key == ord("d"):
        direction = RIGHT
    else:
        direction = NO_MOVE
        
    return direction

def get_exit_status(key):
    """
    function that return exit status from key pressed

    Args:
        key (int): key that got from cv2.waitKey()

    Returns:
        bool: exit status
    """
    
    if key == 27:
        return True
    
    return False