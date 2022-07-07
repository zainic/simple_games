import numpy as np
import cv2
import os, sys

"""
Note : 

All object coordinates are actually top-left corner of the texture
not in the middle

"""

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 720

REAL_WINDOW_WIDTH = 620
REAL_WINDOW_HEIGHT = 680

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
        self.coordinate = np.array([[tuple((i,j)) for i in range(WINDOW_HEIGHT)] for j in range(WINDOW_WIDTH)], dtype='i,i')
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
        
        self.bullet_texture = {}
        self.bullet_texture["main"] = cv2.imread(os.path.join(".", "texture", "main_bullet.png"))
        self.bullet_texture["secondary"] = cv2.imread(os.path.join(".", "texture", "secondary_bullet.png"))
        
        self.current_level = 1
        """
        Initial position and hitbox of the ship
        """
        self.position = (WINDOW_HEIGHT - 64 - 40, WINDOW_WIDTH//2 - 32)
        
        self.ship_hitbox = {}
        self.ship_hitbox["lv1"] = ((self.position[0] + 13, self.position[1] + 8),
                                   (self.position[0] + 64, self.position[1] + 56))
        self.ship_hitbox["lv2"] = ((self.position[0] + 12, self.position[1] + 0),
                                   (self.position[0] + 64, self.position[1] + 64))
        self.ship_hitbox["lv3"] = ((self.position[0] + 14, self.position[1] + 8),
                                   (self.position[0] + 64, self.position[1] + 56))
        
        self.start_position_of_bullet = {}
        self.start_position_of_bullet["1"] = (WINDOW_HEIGHT - 64 - 40 + 16, WINDOW_WIDTH//2 - 32 + 30)
        self.start_position_of_bullet["2"] = (WINDOW_HEIGHT - 64 - 40 + 39, WINDOW_WIDTH//2 - 32 + 12)
        self.start_position_of_bullet["3"] = (WINDOW_HEIGHT - 64 - 40 + 39, WINDOW_WIDTH//2 - 32 + 49)
        
        self.main_bullet = []
        self.secondary_bullet = []
    
    def move_ship(self, direction):
        """
        Move the ship into the direction update the hitbox

        Args:
            direction (array): direction of ship movement
        """
        if self.position[0] + direction[0]*4 + 64 >= WINDOW_HEIGHT and self.position[1] + direction[1]*4 + 64 >= WINDOW_WIDTH:
            pass
        elif self.position[0] + direction[0]*4 <= 0 and self.position[1] + direction[1]*4 <= 0:
            pass
        else:
            self.position = (self.position[0] + direction[0]*4, self.position[1] + direction[1]*4)
            self.start_position_of_bullet["1"] = (self.start_position_of_bullet["1"][0] + direction[0]*4, 
                                                  self.start_position_of_bullet["1"][1] + direction[1]*4)
            self.start_position_of_bullet["2"] = (self.start_position_of_bullet["2"][0] + direction[0]*4, 
                                                  self.start_position_of_bullet["2"][1] + direction[1]*4)
            self.start_position_of_bullet["3"] = (self.start_position_of_bullet["3"][0] + direction[0]*4, 
                                                  self.start_position_of_bullet["3"][1] + direction[1]*4)
        
        self.ship_hitbox["lv1"] = ((self.position[0] + 13, self.position[1] + 8),
                                   (self.position[0] + 64, self.position[1] + 56))
        self.ship_hitbox["lv2"] = ((self.position[0] + 12, self.position[1] + 0),
                                   (self.position[0] + 64, self.position[1] + 64))
        self.ship_hitbox["lv3"] = ((self.position[0] + 14, self.position[1] + 8),
                                   (self.position[0] + 64, self.position[1] + 56))
        
    def shoot_bullet(self):
        """
        Shoot the bullet from the ship
        """
        
        main_bullet = np.array(self.start_position_of_bullet["1"])
        secondary_bullet_1 = np.array(self.start_position_of_bullet["2"])
        secondary_bullet_2 = np.array(self.start_position_of_bullet["3"])
        
        if self.current_level == 1:
            self.main_bullet.insert(0, main_bullet)
        elif self.current_level == 2:
            self.secondary_bullet.insert(0, secondary_bullet_1)
            self.secondary_bullet.insert(0, secondary_bullet_2)
        elif self.current_level >= 3:
            self.main_bullet.insert(0, main_bullet)
            self.secondary_bullet.insert(0, secondary_bullet_1)
            self.secondary_bullet.insert(0, secondary_bullet_2)
        
    
class Enemy:
    """
    Create enemy or swarm of enemy object
    """
    def __init__(self):
        """
        Import the texture of enemy ship
        """
        self.enemy_texture = {}
        self.enemy_texture["type1"] = cv2.imread(os.path.join(".", "texture", "enemy_type_1.png"))
        self.enemy_texture["type2"] = cv2.imread(os.path.join(".", "texture", "enemy_type_2.png"))
        self.enemy_texture["type3"] = cv2.imread(os.path.join(".", "texture", "enemy_type_3.png"))
        
        self.current_enemy_texture = np.copy(self.enemy_texture["type1"])
        
        """
        Set path for the enemy
        """
        self.path = {}
        self.path["1"] = lambda t : (t, 10 + 200 * np.sin(np.deg2rad(t)) + 310 - 10)
        self.path["2"] = lambda t : (t, 10 + 200 * np.cos(np.deg2rad(t + 90)) + 310 - 10)
        self.path["3"] = lambda t : (t + 0.2 * t, 10 + 310 - 10)
        self.path["4"] = lambda t : (t, 10 + 310 + 250 - 10)
        self.path["5"] = lambda t : (t, 10 + 310 - 250 - 10)
        self.path["6"] = lambda t : (t, 10 + 300 - np.abs(t - 300) + 310 - 10)
        self.path["7"] = lambda t : (t, 10 - 300 + np.abs(t - 300) + 310 - 10)
        
        self.enemy_position = []
        self.enemies_position_in_t = []
        self.number_path = np.array([])
        
    def deploy_enemies(self, type_enemy, type_swarm):
        """
        Deploy enemy's swarm or create initial position of enemies

        Args:
            type_enemy (int): type of enemy's texture
            type_swarm (int): type of enemy's swarm
        """
        self.enemy_position_in_t = np.arange(0, -301, -30)
        self.current_enemy_texture = np.copy(self.enemy_texture["type" + str(type_enemy)])
        
        if type_swarm == 1:
            self.enemies_position_in_t = [np.copy(self.enemy_position_in_t), np.copy(self.enemy_position_in_t)]
            self.number_path = np.array([1,2])
        elif type_swarm == 2:
            self.enemies_position_in_t = [np.copy(self.enemy_position_in_t), np.copy(self.enemy_position_in_t), np.copy(self.enemy_position_in_t)]
            self.number_path = np.array([3,4,5])
        elif type_swarm == 3:
            self.enemies_position_in_t = [np.copy(self.enemy_position_in_t), np.copy(self.enemy_position_in_t)]
            self.number_path = np.array([6,7])
            
    def update_enemies_position(self, step = 5):
        """
        Update the enemies position

        Args:
            step (int): step of movement in pixel
        """
        
        for i, _ in enumerate(self.enemies_position_in_t):
            self.enemies_position_in_t[i] += step
        
class Destruction:
    def __init__(self):
        pass