import numpy as np
import cv2
import os, sys
import time
from pygame import mixer
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
    START = False
    
    delay_shoot = 10
    delay_start = 30
    
    mixer.init()
    mixer.music.load(os.path.join(".","sound","menu_music.mp3"))
    mixer.music.play(-1)
    
    ship_shoot = mixer.Sound(os.path.join(".","sound","ship_shoot.mp3"))
    
    st = time.time()
    
    while not START:
        frame = create_main_menu_frame(background)
        
        showed_frame = np.copy(frame[20:REAL_WINDOW_HEIGHT + 20, 10:REAL_WINDOW_WIDTH + 10])
        
        ed = time.time()
        if ed - st <= 1/60:
            time.sleep(1/60 - (ed - st))
            fps = 60
        else:
            fps = round(1/(ed - st))
        cv2.putText(showed_frame, "fps : " + str(fps), (10, REAL_WINDOW_HEIGHT - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
        st = time.time()
        
        cv2.imshow("WarShip Game", showed_frame)
        key = cv2.waitKey(1) & 0xff
        
        if EXIT:
            break
        
        background.move_background(1)
        
        START = get_start_status(pressed_keys)
        EXIT = get_exit_status(key)
    
    mixer.music.load(os.path.join(".","sound","play_music.mp3"))
    mixer.music.play(-1)
    
    while not EXIT:
        delay_shoot -= 1
        
        try:
            frame = create_frame(background, ship, enemy, effect)
        except Exception as e:
            ship.move_ship(np.negative(direction))
            frame = create_frame(background, ship, enemy, effect)
        
        showed_frame = np.copy(frame[20:REAL_WINDOW_HEIGHT + 20, 10:REAL_WINDOW_WIDTH + 10])
        
        cv2.putText(showed_frame, "score : " + str(background.score), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)
        
        if ship.hit:
            put_text_in_the_middle(showed_frame, "GAME OVER", size=2, size_stroke=2)
            put_text_in_the_middle(showed_frame, "Press esc to EXIT the game", size=1, add_height=50)
            put_text_in_the_middle(showed_frame, "Press space to RESTART the game", size=1, add_height=90)
            delay_start -= 1
            if get_start_status(pressed_keys) and delay_start <= 0:
                background.score = 0
                ship = Ship()
                enemy = Enemy()
                effect = Effect()
                delay_start = 30

        ed = time.time()
        if ed - st <= 1/60:
            time.sleep(1/60 - (ed - st))
            fps = 60
        else:
            fps = round(1/(ed - st))
        cv2.putText(showed_frame, "fps : " + str(fps), (10, REAL_WINDOW_HEIGHT - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
        st = time.time()
        
        cv2.imshow("WarShip Game", showed_frame)
        
        key = cv2.waitKey(1) & 0xff
        
        direction = get_direction_from_keys(pressed_keys)
        
        if is_shooting(pressed_keys) and delay_shoot <= 0:
            ship.shoot_bullet()
            mixer.Sound.play(ship_shoot)
            delay_shoot = 15
        
        ship.move_ship(direction)
        background.move_background(1)
        effect.next_state()
        effect.move_effect(1)
        
        enemies_alive = np.sum([len(enemies) for enemies in enemy.enemies_position_in_t])
        if enemies_alive == 0:
            type_enemy = np.random.randint(1,4)
            type_swarm = np.random.randint(1,7)
            speed_step = np.random.randint(2,5)
            number_of_enemy = np.random.randint(10,21)
            enemy.deploy_enemies(type_enemy, type_swarm, number_of_enemy)
        else:
            enemy.update_enemies_position(step = speed_step)
        
        EXIT = get_exit_status(key)
        
    listener.stop()
    

if __name__ == "__main__":
    main()