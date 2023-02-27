import pygame
import random
from .config import SCREEN_HEIGHT, SCREEN_WIDTH, RectObjectCoordinates, PlaneData, RADAR_SIZE
from enum import Enum
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)

class Direction(Enum):
    TOP_RIGHT = 1
    RIGHT = 2
    BOTTOM_RIGHT = 3
    BOTTOM = 4
    BOTTOM_LEFT = 5
    LEFT = 6
    TOP_LEFT = 7
    TOP = 8 
    STAY = 9

RADAR_RED = (255, 0, 0, 80)
RADAR_GREEN = (0, 255, 0, 80)

class RadarRectangle:
    def __init__(self, left: int, top: int, width: int, height: int):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.background_color = RADAR_RED
        
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        self.radar_rect = pygame.Rect(
            self.left,
            self.top,
            self.width,
            self.height
        )
        
        self.surface.fill(self.background_color)
        
    def check_collisions(self, enemies: list):
        return any((self.radar_rect.colliderect(enemy) for enemy in enemies))
    
    def paint_area(self, enemies: list):
        self.background_color = RADAR_GREEN if self.check_collisions(enemies) else RADAR_RED
        self.surface.fill(self.background_color)

class PlaneRadar:
    def __init__(self, size: int, plane_data: PlaneData):
        self.size = size
        self.radar_areas = []
        
        # Go top-left by the amount of the size times the plane dimentions
        start_left = plane_data.left - size * plane_data.width 
        start_top = plane_data.top - size * plane_data.height
        
        for row in range(2*self.size+1):
            for column in range(2*self.size+1):
                current_left = start_left + column*plane_data.width
                current_top = start_top + row*plane_data.height
                
                # If arrived to plane position, continue
                if current_left == plane_data.left and current_top == plane_data.top:
                    continue
                
                radar_area = RadarRectangle(
                    left=current_left,
                    top=current_top,
                    width=plane_data.width,
                    height=plane_data.height)
                
                self.radar_areas.append(radar_area)
    
    def get_radar_states(self, enemies: list):
        state = []
        for area in self.radar_areas:
            rocket_in_area = 1 if area.check_collisions(enemies) else 0
            state.append(rocket_in_area)
        
        return state
    
    def count_radar_areas(self):
        return len(self.radar_areas)

# Define the enemy object by extending pygame.sprite.Sprite
# The surface you draw on the screen is now an attribute of 'enemy'
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("images/missle.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 20)

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
    
    def position(self):
        """Returns rocket's position coordinates."""
        return RectObjectCoordinates(
            left=self.rect.left,
            right=self.rect.right,
            top=self.rect.top,
            bottom=self.rect.bottom
        )

# Define the cloud object by extending pygame.sprite.Sprite
# Use an image for a better-looking sprite
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("images/cloud.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # The starting position is randomly generated
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    # Move the cloud based on a constant speed
    # Remove the cloud when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.right < 0:
            self.kill()

# Define a player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("images/jet.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
    
    @classmethod
    def create_element(cls, left: int, top: int):
        """Method works as another constructor that puts element in given position.
        based on given left and top values.
        """
        super(Player, cls).__init__(cls)
        cls.surf = pygame.image.load("images/jet.png").convert()
        cls.surf.set_colorkey((255, 255, 255), RLEACCEL)
        cls.rect = cls.surf.get_rect()
        
        cls.rect.left = left
        cls.rect.top = top
        
        return cls
    
    def move_up(self):
        self.rect.move_ip(0, -5)
        self._keep_me_on_the_screen()
    
    def move_down(self):
        self.rect.move_ip(0, 5)
        self._keep_me_on_the_screen()
    
    def move_left(self):
        self.rect.move_ip(-5, 0)
        self._keep_me_on_the_screen()
    
    def move_right(self):
        self.rect.move_ip(5, 0)
        self._keep_me_on_the_screen()
        
    def get_rect_size(self):
        return self.rect.width, self.rect.height # (62, 25)
    
    def _keep_me_on_the_screen(self):
        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH - RADAR_SIZE*self.rect.width:
            self.rect.right = SCREEN_WIDTH - RADAR_SIZE*self.rect.width
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT - RADAR_SIZE*self.rect.height:
            self.rect.bottom = SCREEN_HEIGHT - RADAR_SIZE*self.rect.height
    
    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)
            
        # Keep player on the screen
        self._keep_me_on_the_screen()

    def position(self):
        """Returns player's position coordinates."""
        return RectObjectCoordinates(
            left=self.rect.left,
            right=self.rect.right,
            top=self.rect.top,
            bottom=self.rect.bottom
        )
    
    def move(self, direction: Direction):
        if direction == Direction.TOP_RIGHT:
                self.move_up()
                self.move_right()
        elif direction == Direction.RIGHT:
                self.move_right()
        elif direction == Direction.BOTTOM_RIGHT:
                self.move_down()
                self.move_right()
        elif direction == Direction.BOTTOM:
                self.move_down()
        elif direction == Direction.BOTTOM_LEFT:
                self.move_left()
                self.move_down()
        elif direction == Direction.LEFT:
                self.move_left()
        elif direction == Direction.TOP_LEFT:
                self.move_up()
                self.move_left()
        elif direction == Direction.TOP:
                self.move_up()
        elif direction == Direction.STAY:
            pass