from turtle import position
import numpy as np
import cv2
import sys
import os

UP = np.array([0, -1])
DOWN = np.array([0, 1])
LEFT = np.array([-1, 0])
RIGHT = np.array([1, 0])

class Background:
    """Create area to play the game"""
    def __init__(self, width = 5, height = 5, style = 'grass'):
        """Set width, height, and style"""
        if width <= 3 or height <= 3:
            raise AssertionError("The board is too small") # Cant play with small board
        self.width = width
        self.height = height
        self.style = style
    
    def create_background(self):
        """Set backround style"""
        self.pixel = cv2.imread(os.path.join(".", "texture", self.style + ".png")) # importing 16 by 16 square image
        if self.pixel is None:
            raise AssertionError("Invalid style option") # if the style isn't available

        """Create background from 16 by 16 image"""
        self.background = np.vstack([np.hstack([self.pixel for i in range(self.width)]) for j in range(self.height)])
        
        """Create coordinates"""
        self.coordinate = {}
        x_coords = np.arange(7, 16 * self.width, 16)
        y_coords = np.arange(7, 16 * self.height, 16)
        for j,y in enumerate(y_coords):
            for i,x in enumerate(x_coords):
                self.coordinate[(i,j)] = (x,y)

class Snake:
    """Create Snake Object"""
    def __init__(self, width = 5, height = 5, style = 'grass'):
        """Initial position and direction"""
        self.width = width
        self.height = height
        
        self.initial_direction = RIGHT
        self.initial_position = np.array([np.array([self.width//2 - 2, self.height//2 - 2]),
                                          np.array([self.width//2 - 2, self.height//2 - 1]),
                                          np.array([self.width//2 - 1, self.height//2 - 1])])
        
        self.position = self.initial_position
        self.direction = self.initial_direction  
        self.style = style
        
    def create_snake_texture(self):
        self.texture = {}
        temp_body1_texture = cv2.imread(os.path.join(".", "snake_texture", self.style,  "body_1.png"))
        temp_body2_texture = cv2.imread(os.path.join(".", "snake_texture", self.style,  "body_2.png"))
        temp_head_texture = cv2.imread(os.path.join(".", "snake_texture", self.style,  "head.png"))
        
        self.texture["body_1"] = np.copy(temp_body1_texture)
        self.texture["body_2"] = np.copy(temp_body2_texture)
        self.texture["head"] = np.copy(temp_head_texture)
        
        self.texture["body_1"][np.where((temp_body1_texture == [255,255,255]).all(axis=2))] = [0,0,0]
        self.texture["body_2"][np.where((temp_body2_texture == [255,255,255]).all(axis=2))] = [0,0,0]
        self.texture["head"][np.where((temp_head_texture == [255,255,255]).all(axis=2))] = [0,0,0]
    
    def move(self, direction):
        """Update the position of the snake"""
        self.direction = direction
        self.position = np.concatenate((self.position[1:], [self.position[-1] + self.direction]))
        
    def grow(self, direction):
        """grow the snake adapting the snake direction"""
        self.direction = direction
        self.position = np.concatenate((self.position, [self.position[-1] + self.direction]))

class Food:
    """Create Food Object"""
    def __init__(self, width = 5, height = 5, style = 'grass'):
        """Initial food condition"""
        self.width = width
        self.height = height
        self.style = style
        self.food_coords = np.array([(np.random.randint(0, self.width),
                                      np.random.randint(0, self.height))])
        
    def create_food_texture(self):
        temp_food_texture = cv2.imread(os.path.join(".", "food_texture", self.style + ".png"))
        self.texture = np.copy(temp_food_texture)
        self.texture[np.where((temp_food_texture == [255,255,255]).all(axis=2))] = [0,0,0]
        
    def spawn_food(self):
        x = np.random.randint(0,self.width)
        y = np.random.randint(0,self.height)
        self.food_coords = np.concatenate((self.food_coords, np.array([(x,y),])))
        
    def remove_food(self):
        if len(self.food_coords) > 5:
            self.food_coords = np.delete(self.food_coords, np.random.randint(0,2), axis=0)
            
    def remove_food_from_coords(self, coord):
        i = np.where((self.food_coords == coord).all(axis=1))
        self.food_coords = np.delete(self.food_coords, i, axis=0)

def get_direction(current_direction):
    """
    Update direction from user input
    w => UP
    a => DOWN
    d => RIGHT
    a => LEFT
    """
    press = cv2.waitKey(50) & 0xff
    direction = current_direction
    """
    Note : Snake can't go backward
    ex : if the current snake direction is UP, player can't input DOWN ("s")
    """
    if current_direction[0] == 1 and current_direction[1] == 0:
        if press == ord("w"):
            direction = UP
        elif press == ord("s"):
            direction = DOWN
    elif current_direction[0] == -1 and current_direction[1] == 0:
        if press == ord("w"):
            direction = UP
        elif press == ord("s"):
            direction = DOWN
    elif current_direction[0] == 0 and current_direction[1] == 1:
        if press == ord("a"):
            direction = LEFT
        elif press == ord("d"):
            direction = RIGHT
    elif current_direction[0] == 0 and current_direction[1] == -1:
        if press == ord("a"):
            direction = LEFT
        elif press == ord("d"):
            direction = RIGHT
        
    if press == 27:
        exit = True
    else:
        exit = False
        
    return direction, exit 

def get_frame(background, snake, food):
    """
    Create frame from current condition of snake

    Args:
        background (Background): Background class
        snake (Snake): Snake class
        food (Food): Food class

    Returns:
        ndarray: frame of condition
    """
    frame = np.copy(background.background)
    
    food_texture = food.texture
    body1_texture = snake.texture["body_1"]
    body2_texture = snake.texture["body_2"]
    head_texture = snake.texture["head"]
    
    pixel_minus_food = np.copy(background.pixel)
    pixel_minus_food[np.where((food_texture != [0,0,0]).all(axis=2))] = [0,0,0]
        
    coordinate = background.coordinate
    
    # Food frame
    food_coords = food.food_coords
    for coord in food_coords:
        position = coordinate[tuple(coord)]
        frame[position[1] - 7:position[1] + 9, position[0] - 7:position[0] + 9] = pixel_minus_food + food_texture
    
    # Snake (body) frame
    head = snake.position[-1]
    body = snake.position[:-1]
    alternate = 0
    for N, coord in enumerate(body):
        position = coordinate[tuple(coord)]
        for sub in np.arange(0, 15, 2):
            sub_position = position + (snake.position[N+1] - coord) * sub 
            pixel_minus_body = np.copy(frame[sub_position[1] - 7:sub_position[1] + 9, sub_position[0] - 7:sub_position[0] + 9])
            if alternate % 2 == 0:
                pixel_minus_body[np.where((body1_texture != [0,0,0]).all(axis=2))] = [0,0,0]
                frame[sub_position[1] - 7:sub_position[1] + 9, sub_position[0] - 7:sub_position[0] + 9] = pixel_minus_body + body1_texture
            else:
                pixel_minus_body[np.where((body2_texture != [0,0,0]).all(axis=2))] = [0,0,0]
                frame[sub_position[1] - 7:sub_position[1] + 9, sub_position[0] - 7:sub_position[0] + 9] = pixel_minus_body + body2_texture
            alternate += 1
    
    # Snake (head) frame    
    position = coordinate[tuple(head)]
    pixel_minus_head = np.copy(frame[position[1] - 7:position[1] + 9, position[0] - 7:position[0] + 9])
    pixel_minus_head[np.where((head_texture != [0,0,0]).all(axis=2))] = [0,0,0]
    frame[position[1] - 7:position[1] + 9, position[0] - 7:position[0] + 9] = pixel_minus_head + head_texture
    
    # Scoreboard
    score = len(snake.position) - 3
    text_width, text_height = cv2.getTextSize("Score : " + str(score), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cv2.LINE_AA)[0]
    cv2.putText(frame, "Score : " + str(score), (10, text_height+10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
    
    return frame

def check(array_list, tupl):
    """
    Checking if tuple (1 x 2) is in array_list (n x 2)

    Args:
        array_list (ndarray): list of array (n x 2)
        tupl (tuple): tuple for check if it was in array list (1 x 2)

    Returns:
        boolean : True or False
    """
    for i,j in array_list:
        if i == tupl[0] and j == tupl[1]:
            return True
        
    return False

def check_uniqueness(array_list):
    """
    Checking if every tuple (1 x 2) is unique in array_list (n x 2)

    Args:
        array_list (ndarray): list of array (n x 2)

    Returns:
        boolean : True or False
    """
    dicts = {}
    for i,j in array_list:
        if (i,j) in dicts.keys():
            return False
        else:
            dicts[(i,j)] = True
    return True

def main():
    try:
        background = Background(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
        snake = Snake(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
        food = Food(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    except IndexError:
        raise AssertionError("Need exactly 3 input (width, height, style)")
    
    background.create_background()
    snake.create_snake_texture()
    food.create_food_texture()
    
    i = 0
    exit = False
    
    while not exit:
        try:
            frame = get_frame(background, snake, food)
        except:
            break
        
        if not check_uniqueness(snake.position):
            break
        
        cv2.imshow("Snake Game", frame)
        direction, exit = get_direction(snake.direction)
        
        i += 1
        if i % 10 == 9:
            food.spawn_food()
        elif i % 10 == 5:
            food.remove_food()
            
        head = snake.position[-1]
        if check(food.food_coords,head):
            snake.grow(direction)
            food.remove_food_from_coords(head)
        else:
            snake.move(direction)
    
    text_width, text_height = cv2.getTextSize("GAME OVER", cv2.FONT_HERSHEY_SIMPLEX, 1, cv2.LINE_AA)[0]
    CenterCoordinates = (int(frame.shape[1] / 2)-int(text_width / 2), int(frame.shape[0] / 2) - int(text_height / 2))
    cv2.putText(frame, "GAME OVER", CenterCoordinates, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)
    cv2.imshow("Snake Game", frame)
    cv2.waitKey(0)    
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()