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
        self.coordinate = np.array([[tuple((i,j)) for i in range(WINDOW_WIDTH)] for j in range(WINDOW_HEIGHT)], dtype='i,i')
        self.i = int(0)
        self.score = 0
        
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
        
        self.hit = False
        
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
        
        self.main_bullet = np.array([], dtype='i,i')
        self.secondary_bullet = np.array([], dtype='i,i')
    
    def move_ship(self, direction):
        """
        Move the ship into the direction update the hitbox

        Args:
            direction (array): direction of ship movement
        """
        if self.position[0] + direction[0]*4 + 64 >= REAL_WINDOW_HEIGHT + 20 or self.position[1] + direction[1]*4 + 64 >= REAL_WINDOW_WIDTH + 10:
            pass
        elif self.position[0] + direction[0]*4 <= 20 or self.position[1] + direction[1]*4 <= 10:
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
        
        main_bullet = np.array([self.start_position_of_bullet["1"]], dtype='i,i')
        secondary_bullet_1 = np.array([self.start_position_of_bullet["2"]], dtype='i,i')
        secondary_bullet_2 = np.array([self.start_position_of_bullet["3"]], dtype='i,i')
        
        if self.current_level == 1:
            self.main_bullet = np.concatenate([main_bullet, self.main_bullet])
        elif self.current_level == 2:
            self.secondary_bullet = np.concatenate([secondary_bullet_2, self.secondary_bullet])
            self.secondary_bullet = np.concatenate([secondary_bullet_1, self.secondary_bullet])
        elif self.current_level >= 3:
            self.main_bullet = np.concatenate([main_bullet, self.main_bullet])
            self.secondary_bullet = np.concatenate([secondary_bullet_2, self.secondary_bullet])
            self.secondary_bullet = np.concatenate([secondary_bullet_1, self.secondary_bullet])
        
    
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
        
class Effect:
    """
    Create state of effect object like destruction of the ship
    """
    def __init__(self):
        """
        Import the texture of effect
        It forms list of event image
        """
        self.full_effects = {}
        self.full_effects["explosive"] = cv2.imread(os.path.join(".", "texture", "explosive.png"))
        self.full_effects["death_ship"] = cv2.imread(os.path.join(".", "texture", "death_ship.png"))
        
        self.effects = {}
        self.effects["explosive"] = np.split(self.full_effects["explosive"], 
                                             self.full_effects["explosive"].shape[0]//self.full_effects["explosive"].shape[1])
        self.effects["death_ship"] = np.split(self.full_effects["death_ship"], 
                                             self.full_effects["death_ship"].shape[0]//self.full_effects["death_ship"].shape[1])
        
        self.effect_size = {}
        self.effect_size["explosive"] = self.effects["explosive"][0].shape[:2]
        self.effect_size["death_ship"] = self.effects["death_ship"][0].shape[:2]
        
        """
        Initial condition
        """ 
        self.effect_coordinates = {}
        self.effect_coordinates["explosive"] = {}
        self.effect_coordinates["death_ship"] = {}
        
    def next_state(self):
        """
        Next state of explosion
        """
        removed_state = []
        
        for key in self.effect_coordinates.keys():
            for coord in self.effect_coordinates[key].keys():
                 self.effect_coordinates[key][coord] += 1
                 if self.effect_coordinates[key][coord] >= len(self.effects[key]):
                    removed_state.append((key, coord))
        
        for key, coord in removed_state:
            self.effect_coordinates[key].pop(coord)
    
    def explode(self, coordinates):
        """
        Create explosion from coordinates

        Args:
            coordinates (tuple): coordinates of explosion in pixel
        """
        self.effect_coordinates["explosive"][coordinates] = 0
    
    def destroy_ship(self, coordinates):
        """
        Destroy explosion in 

        Args:
            coordinates (tuple): coordinates of explosion in pixel
        """
        self.effect_coordinates["death_ship"][coordinates] = 0
        
    def move_effect(self, step):
        """
        Move the effect texture following the background

        Args:
            step (int): step of movement
        """
        changed_state = []
        
        for key in self.effect_coordinates.keys():
            for coord in self.effect_coordinates[key].keys():
                next_coord = (coord[0] + step, coord[1])
                changed_state.append((key, coord, next_coord))
        
        for key, coord, next_coord in changed_state:
            self.effect_coordinates[key][next_coord] = self.effect_coordinates[key][coord]
            self.effect_coordinates[key].pop(coord)
            
            