from ast import excepthandler
from telnetlib import KERMIT
from matplotlib import is_interactive
import numpy as np
import cv2
import os, sys

from object import *
from pynput import keyboard

def put_text_in_the_middle(frame, text = "Sample Text", size = 1, size_stroke=1, style = cv2.FONT_HERSHEY_SIMPLEX, line = cv2.LINE_AA, add_height=0):
    """
    Place text in the middle of screen as default

    Args:
        frame (ndarray): image that want to be overlayed by text
        text (str, optional): Text. Defaults to "Sample Text".
        size (int, optional): size of text. Defaults to 1.
        size_stroke (int, optional): size stroke of text. Defaults to 1.
        style (any, optional): font style. Defaults to cv2.FONT_HERSHEY_SIMPLEX.
        line (ant, optional): line style. Defaults to cv2.LINE_AA.
        add_height (int, optional): control the height with middle as origin. Defaults to 0.

    Returns:
        ndarray: image with the text in it
    """
    text_width, text_height = cv2.getTextSize(text, style, size, line)[0]
    CenterCoordinates = (frame.shape[1] // 2 - text_width // 2 + 8,
                         frame.shape[0] // 2 + text_height // 2 + int(add_height))
    cv2.putText(frame, text, CenterCoordinates, style, size, (255,255,255), size_stroke, line)
    return frame

def check_intersection(array1, array2):
    """
    Check if 2 arrays have common elements

    Args:
        array1 (ndarray): numpy array with tuples as elements 
        array2 (ndarray): numpy array with tuples as elements 

    Returns:
        bool: boolean
    """
    check = np.in1d(array1, array2)
    is_intersect = check.any()
    
    return is_intersect

def create_frame(background, ship, enemy, effect):
    """
    Create one frame from the condition

    Args:
        background (class Background): background of the game
        ship (class Ship): ship that player control
        enemy (class Enemy): enemy that attack player
        effect (class Effect): effect of things happen

    Returns:
        ndarray: image of the current condition
    """
    
    hit = False
    
    frame = np.copy(background.background)
    
    # Get the coordinates of every object
    ship_position = np.copy(ship.position)
    copy_of_main_bullets_pos = np.copy(ship.main_bullet)
    copy_of_secondary_bullets_pos = np.copy(ship.secondary_bullet)
    enemies_position = np.copy(enemy.enemies_position_in_t)
    
    # Get texture early
    enemy_texture = np.copy(enemy.current_enemy_texture)
    ship_texture = np.copy(ship.ship_texture["lv" + str(ship.current_level)])
    
    # Show effect
    for key in effect.effect_coordinates.keys():
        effect_texture = np.copy(effect.effects[key])
        for position, i in effect.effect_coordinates[key].items():
            try:
                part_fx = np.copy(frame[position[0] : position[0] + effect_texture[i].shape[0], 
                                        position[1] : position[1] + effect_texture[i].shape[1]])
                part_fx_overlay = cv2.addWeighted(part_fx, 1, effect_texture[i], 1, 0)
                frame[position[0] : position[0] + effect_texture[i].shape[0], position[1] : position[1] + effect_texture[i].shape[1]] = part_fx_overlay
            except:
                continue
        
    # Show bullet
    deleted_bullet = []
    texture = np.copy(ship.bullet_texture["main"])
    for i, position in enumerate(copy_of_main_bullets_pos):
        try:
            part_minus_bullet = np.copy(frame[position[0] : position[0] + texture.shape[0], position[1] : position[1] + texture.shape[1]])
            part_minus_bullet[np.where((texture != [0, 0, 0]).all(axis=2))] = [0, 0, 0]
            frame[position[0] : position[0] + texture.shape[0], position[1] : position[1] + texture.shape[1]] = part_minus_bullet + texture
            ship.main_bullet[i] = tuple(np.array([ship.main_bullet[i][0], ship.main_bullet[i][1]]) + UP * 6)
        except Exception as e:
            deleted_bullet.append(i)
    
    texture = np.copy(ship.bullet_texture["secondary"])
    for i, position in enumerate(copy_of_secondary_bullets_pos):
        try:
            part_minus_bullet = np.copy(frame[position[0] : position[0] + texture.shape[0], position[1] : position[1] + texture.shape[1]])
            part_minus_bullet[np.where((texture != [0, 0, 0]).all(axis=2))] = [0, 0, 0]
            frame[position[0] : position[0] + texture.shape[0], position[1] : position[1] + texture.shape[1]] = part_minus_bullet + texture
            ship.secondary_bullet[i] = tuple(np.array([ship.secondary_bullet[i][0], ship.secondary_bullet[i][1]]) + UP * 6)
        except Exception as e:
            deleted_bullet.append(i + len(copy_of_main_bullets_pos))
    
    # Show ship
    if not ship.hit:
        part_minus_ship = np.copy(frame[ship_position[0] : ship_position[0] + 64, ship_position[1] : ship_position[1] + 64])
        part_minus_ship[np.where((ship_texture != [0, 0, 0]).all(axis=2))] = [0, 0, 0]
        frame[ship_position[0] : ship_position[0] + 64, ship_position[1] : ship_position[1] + 64] = part_minus_ship + ship_texture
    
    # Show enemies ship
    enemies_alive = np.sum([len(enemies) for enemies in enemy.enemies_position_in_t])
    deleted_enemy = []
        
    bullet_positions = np.concatenate([copy_of_main_bullets_pos, copy_of_secondary_bullets_pos])
    
    if enemies_alive > 0:
        for number, enemies_path in enumerate(enemies_position):
            for i, t_value in enumerate(enemies_path):
                position = np.int32(enemy.path[str(enemy.number_path[number])](t_value))
                hit = False
                
                if position[0] < 0 or position[0] >= 700:
                    if position[0] >= 700:
                        deleted_enemy.append((number, t_value))
                    continue
                
                # Check if bullet hits enemy
                for j, pos in enumerate(bullet_positions):
                    
                    if j < len(copy_of_main_bullets_pos):
                        bullet_texture = np.copy(ship.bullet_texture["main"])
                    else:
                        bullet_texture = np.copy(ship.bullet_texture["secondary"])
                    
                    if not (position[1] - bullet_texture.shape[1] <= pos[1] <= position[1] + bullet_texture.shape[1] + enemy_texture.shape[1] and position[0] - bullet_texture.shape[0] <= pos[0] <= position[0] + bullet_texture.shape[0] + enemy_texture.shape[0]):
                        continue
                    else:
                        try:
                            bullet_coords = np.copy(background.coordinate[pos[0] : pos[0] + bullet_texture.shape[0], pos[1] : pos[1] + bullet_texture.shape[1]])
                            enemy_coords = np.copy(background.coordinate[position[0] : position[0] + enemy_texture.shape[0], position[1] : position[1] + enemy_texture.shape[1]])
                            bullet_coords[np.where((bullet_texture == [0, 0, 0]).all(axis=2))] = (-1,-1)
                            enemy_coords[np.where((enemy_texture == [0, 0, 0]).all(axis=2))] = (-1,-1)
                            flatten_bullet_coords = np.concatenate(bullet_coords)
                            flatten_enemy_coords = np.concatenate(enemy_coords)
                            flatten_bullet_coords_cropped = np.delete(flatten_bullet_coords, np.argwhere(flatten_bullet_coords == np.array((-1,-1), dtype="i,i")))
                            flatten_enemy_coords_cropped = np.delete(flatten_enemy_coords, np.argwhere(flatten_enemy_coords == np.array((-1,-1), dtype="i,i")))
                            if check_intersection(flatten_bullet_coords_cropped, flatten_enemy_coords_cropped):
                                deleted_bullet.append(j)
                                background.score += 1
                                hit = True
                                break
                        except Exception as e:
                            continue
                        
                # Check if enemy hits ship
                if not (ship_position[1] - enemy_texture.shape[1] <= position[1] < ship_position[1] + enemy_texture.shape[1] + ship_texture.shape[1] and ship_position[0] - enemy_texture.shape[0] <= position[0] < ship_position[0] + enemy_texture.shape[0] + ship_texture.shape[0]):
                    pass
                elif not ship.hit:
                    try:
                        ship_coords = np.copy(background.coordinate[ship_position[0] : ship_position[0] + ship_texture.shape[0], ship_position[1] : ship_position[1] + ship_texture.shape[1]])
                        enemy_coords = np.copy(background.coordinate[position[0] : position[0] + enemy_texture.shape[0], position[1] : position[1] + enemy_texture.shape[1]])
                        ship_coords[np.where((ship_texture == [0, 0, 0]).all(axis=2))] = (-1,-1)
                        enemy_coords[np.where((enemy_texture == [0, 0, 0]).all(axis=2))] = (-1,-1)
                        flatten_ship_coords = np.concatenate(ship_coords)
                        flatten_enemy_coords = np.concatenate(enemy_coords)
                        flatten_ship_coords_cropped = np.delete(flatten_ship_coords, np.argwhere(flatten_ship_coords == np.array((-1,-1), dtype="i,i")))
                        flatten_enemy_coords_cropped = np.delete(flatten_enemy_coords, np.argwhere(flatten_enemy_coords == np.array((-1,-1), dtype="i,i")))
                        if check_intersection(flatten_ship_coords_cropped, flatten_enemy_coords_cropped):
                            ship.hit = True
                            hit = True
                            ship_explosion_position = (ship_position[0] - (effect.effect_size["death_ship"][0] - ship_texture.shape[0]) // 2,
                                                       ship_position[1] - (effect.effect_size["death_ship"][1] - ship_texture.shape[1]) // 2)
                            effect.destroy_ship(ship_explosion_position)
                    except Exception as e:
                        pass
                    
                if hit:
                    explosion_position = (position[0] - (effect.effect_size["explosive"][0] - enemy_texture.shape[0]) // 2,
                                          position[1] - (effect.effect_size["explosive"][1] - enemy_texture.shape[1]) // 2)
                    effect.explode(explosion_position)
                    deleted_enemy.append((number, t_value))
                    continue
                    
                try:
                    part_minus_enemy = np.copy(frame[position[0] : position[0] + enemy_texture.shape[0], position[1] : position[1] + enemy_texture.shape[1]])
                    part_minus_enemy[np.where((enemy_texture != [0, 0, 0]).all(axis=2))] = [0, 0, 0]
                    frame[position[0] : position[0] + enemy_texture.shape[0], position[1] : position[1] + enemy_texture.shape[1]] = part_minus_enemy + enemy_texture
                except Exception as e:
                    if position[0] >= 700:
                        deleted_enemy.append((number, t_value))

    for number, t_value in sorted(deleted_enemy, key = lambda a : a[1], reverse=True):
        T = enemy.enemies_position_in_t[number]
        enemy.enemies_position_in_t[number] = np.delete(T, np.where(T == t_value))

    for i in sorted(deleted_bullet, reverse=True):
        if i < len(copy_of_main_bullets_pos):
            ship.main_bullet = np.delete(ship.main_bullet, i)
        else:
            ship.secondary_bullet = np.delete(ship.secondary_bullet, i - len(copy_of_main_bullets_pos))
    
    return frame

def create_main_menu_frame(background):
    """
    Create one frame of main menu

    Args:
        background (class Background): background of the game

    Returns:
        ndarray: image of the menu
    """
    frame = np.copy(background.background)
    
    logo = background.logo 
    
    position = (frame.shape[0] // 2 - logo.shape[0] // 2 - 50,frame.shape[1] // 2 - logo.shape[1] // 2)
    
    part_logo = np.copy(frame[position[0] : position[0] + logo.shape[0], position[1] : position[1] + logo.shape[1]])
    part_logo_overlay = cv2.addWeighted(part_logo, 1, logo, 1, 0)
    frame[position[0] : position[0] + logo.shape[0], position[1] : position[1] + logo.shape[1]] = part_logo_overlay
    
    frame = put_text_in_the_middle(frame, "Press space to START the game", size=1,  size_stroke=2, add_height=100)
    
    return frame

def get_direction_from_keys(keys):
    """
    function that return direction for ship from key pressed

    Args:
        keys (set): keys that got from Listener

    Returns:
        array: direction 
    """
    
    direction = np.copy(NO_MOVE)
    
    if keyboard.KeyCode.from_char("w") in keys:
        direction += UP
    if keyboard.KeyCode.from_char("s") in keys:
        direction += DOWN
    if keyboard.KeyCode.from_char("a") in keys:
        direction += LEFT
    if keyboard.KeyCode.from_char("d") in keys:
        direction += RIGHT
        
    return direction

def is_shooting(keys):
    """
    Checking if player was shooting by pressing space button

    Args:
        keys (set): keys that got from Listener

    Returns:
        bool: shooting status 
    """
    if keyboard.Key.space in keys:
        return True
    
    return False

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

def get_start_status(keys):
    """
    function that return exit status from key pressed

    Args:
        key (int): key that got from cv2.waitKey()

    Returns:
        bool: exit status
    """
    
    if keyboard.Key.space in keys:
        return True
    
    return False