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
    effect = Effect()
    
    listener = keyboard.Listener(on_press=on_pressed, on_release=on_released)
    listener.start()
    
    EXIT = False
    
    delay_shoot = 10
    
    while not EXIT:
        delay_shoot -= 1
        
        try:
            frame = create_frame(background, ship, enemy, effect)
        except Exception as e:
            ship.move_ship(np.negative(direction))
            frame = create_frame(background, ship, enemy, effect)
        
        showed_frame = frame[20:REAL_WINDOW_HEIGHT + 20, 10:REAL_WINDOW_WIDTH + 10]
        
        cv2.imshow("WarShip Game", showed_frame)
        key = cv2.waitKey(10) & 0xff
        
        direction = get_direction_from_keys(pressed_keys)
        
        if is_shooting(pressed_keys) and delay_shoot <= 0:
            ship.shoot_bullet()
            delay_shoot = 10
        
        ship.move_ship(direction)
        background.move_background(1)
        effect.next_state()
        
        enemies_alive = np.sum([len(enemies) for enemies in enemy.enemies_position_in_t])
        if enemies_alive == 0:
            type_enemy = np.random.randint(1,4)
            type_swarm = np.random.randint(1,4)
            speed_step = np.random.randint(2,5)
            enemy.deploy_enemies(type_enemy, type_swarm)
        else:
            enemy.update_enemies_position(step = speed_step)
        
        EXIT = get_exit_status(key)
        
    listener.stop()

if __name__ == "__main__":
    main()