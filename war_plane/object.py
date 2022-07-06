import numpy as np
import cv2
import os, sys

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 720

UP = np.array([-1, 0])
DOWN = np.array([1, 0])
LEFT = np.array([0, -1])
RIGHT = np.array([0, 1])
NO_MOVE = np.array([0, 0])

class Background:
    """
    Create background of the game
    """
    def __init__(self):
        """
        Import the background from local file and preprocessing
        """
        self.full_background = cv2.imread(os.path.join(".", "texture", "background.png"))
        self.background = self.full_background[:WINDOW_HEIGHT, :]
        self.coordinate = np.array([(i,j) for i in range(WINDOW_HEIGHT) for j in range(WINDOW_WIDTH)])
        self.i = int(0)
        
    def move_background(self, step):
        """
        Move the background, so added the dynamic background

        Args:
            step (int): speed of movement in pixel
        """
        self.i = (self.i - step) % 1440
        if (self.i % 1440) + WINDOW_HEIGHT >= 1440:
            self.background = np.vstack([self.full_background[self.i :, :], self.full_background[:WINDOW_HEIGHT - (1440 - self.i), :]])
        else:
            self.background = self.full_background[self.i : self.i + WINDOW_HEIGHT, :]
        
class Ship:
    """
    Create ship object
    """
    def __init__(self):
        """
        Import the texture of war ship
        """
        self.ship_texture = {}
        self.ship_texture["lv1"] = cv2.imread(os.path.join(".", "texture", "ship_level_1.png"))
        self.ship_texture["lv2"] = cv2.imread(os.path.join(".", "texture", "ship_level_2.png"))
        self.ship_texture["lv3"] = cv2.imread(os.path.join(".", "texture", "ship_level_3.png"))
        
        self.current_level = 1
        """
        Initial position of the ship
        """
        self.position = (WINDOW_HEIGHT - 64 - 20, WINDOW_WIDTH//2 - 32)
    
    def move_ship(self, direction):
        """
        Move the ship into the direction

        Args:
            direction (array): direction of ship movement
        """
        if self.position[0] + direction[0]*4 + 64 >= WINDOW_HEIGHT and self.position[1] + direction[1]*4 + 64 >= WINDOW_WIDTH:
            pass
        elif self.position[0] + direction[0]*4 <= 0 and self.position[1] + direction[1]*4 <= 0:
            pass
        else:
            self.position = (self.position[0] + direction[0]*4, self.position[1] + direction[1]*4)
        
    def shoot_bullet(self):
        """
        Shoot the bullet from the ship
        """
        
        if self.current_level == 1:
            pass
        elif self.current_level == 2:
            pass
        elif self.current_level >= 3:
            pass
        
    
class Enemy:
    """
    Create enemy or swarm of enemy object
    """
    def __init__(self):
        pass