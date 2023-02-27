# Import the pygame module
import pygame
from src.game_utils.game_objects import Enemy, Player, Cloud, RadarRectangle, PlaneRadar, PlaneData
from src.game_utils.config import SCREEN_WIDTH, SCREEN_HEIGHT, RADAR_SIZE, RectObjectCoordinates, RadarSquares, SPEED
from src.game_utils.game_objects import Direction
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# Initialize pygame
pygame.init()

class FlightGame:
    # Define constants for the screen width and height
    
    def __init__(self):
        # Setup the clock for a decent framerate
        self.clock = pygame.time.Clock()
        # Create the screen object
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Create a custom event for adding a new enemy and cloud
        self.ADDENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ADDENEMY, 250)
        self.ADDCLOUD = pygame.USEREVENT + 2
        pygame.time.set_timer(self.ADDCLOUD, 1000)
        
        self.reset()
        
    def reset(self):
        self.direction = Direction.STAY
        self.score = 0
        
        # Create groups to hold enemy sprites and all sprites
        # - enemies is used for collision detection and position updates
        # - all_sprites is used for rendering
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        
        # Instantiate player
        self.player = Player()
        self.all_sprites.add(self.player)
        self.update_plane_data()
        
        # Create plane radar
        self.radar = PlaneRadar(
                size = RADAR_SIZE,
                plane_data=self.plane_data
            )
        
        self.destroy_rockets()
        
    def destroy_rockets(self):
        for enemy in self.enemies:
            enemy.kill()
    
    def update_plane_data(self):
        self.plane_data = PlaneData(
                left=self.player.rect.left,
                top=self.player.rect.top,
                width=self.player.rect.width,
                height=self.player.rect.height,
            )
    
    def _move(self, action):
        # Action
        # Array of 0s and 1s where 1 is move to be taken
        # There can be just one 1 in the array
        # [top-right, right, bottom-right,
        # bottom, bottom-left, left,
        # top-left, top, no-move
        clock_wise_directions = [
            Direction.TOP_RIGHT,
            Direction.RIGHT,
            Direction.BOTTOM_RIGHT,
            Direction.BOTTOM,
            Direction.BOTTOM_LEFT,
            Direction.LEFT,
            Direction.TOP_LEFT,
            Direction.TOP,
            Direction.STAY,
        ]
        
        self.direction = action.index(1)
        self.player.move(clock_wise_directions[self.direction])
    
    def play_step(self, action):
        # Move
        self._move(action)
        
        # Check if game is over
        reward = 0 # rocket gone: +1, game over: -10, else: 0
        game_over = False
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            # If so, then remove the player and stop the loop
            self.player.kill()
            game_over = True
            reward = -10
            return reward, game_over, self.score
    
        # update ui and clock
        reward,game_over,self.score = self._update_ui()
        return reward,game_over,self.score
    
    def _update_ui(self):
        # for loop through the event queue
        for event in pygame.event.get():
            # Add a new enemy
            if event.type == self.ADDENEMY:
                # Create the new enemy and add it to sprite groups
                new_enemy = Enemy()
                self.enemies.add(new_enemy)
                self.all_sprites.add(new_enemy)
            # Add a new cloud
            elif event.type == self.ADDCLOUD:
                # Create the new cloud and add it to sprite groups
                new_cloud = Cloud()
                self.clouds.add(new_cloud)
                self.all_sprites.add(new_cloud)
        
        self.screen.fill((135, 206, 250))
        
        rockets_before_movement = len(self.enemies)
        self.enemies.update()
        rockets_after_movement = len(self.enemies)
        
        self.update_plane_data()
        self.radar = PlaneRadar(
                size = RADAR_SIZE,
                plane_data=self.plane_data
            )
        
        for area in self.radar.radar_areas:
            area.paint_area(self.enemies)
            self.screen.blit(area.surface, area.radar_rect)
        
        for entity in self.all_sprites:
            self.screen.blit(entity.surf, entity.rect)
        
        # Check if any enemies have collided with the player
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            # If so, then remove the player and stop the loop
            self.player.kill()
            game_over = True
            reward = -20
            return reward,game_over,self.score
        
        # Update the display
        pygame.display.flip()
        
        self.clock.tick(SPEED)

        reward = abs(rockets_after_movement-rockets_before_movement)
        game_over = False
        self.score += reward
        return reward,game_over,self.score
    
    def run(self, radar: bool = False):
        running = True
        
        # Main loop
        while running:
            # loop through the event queue
            for event in pygame.event.get():
                # Check for KEYDOWN event
                if event.type == KEYDOWN:
                    # If the Esc key is pressed, then exit the main loop
                    if event.key == K_ESCAPE:
                        running = False
                # Check for QUIT event. If QUIT, then set running to false.
                elif event.type == QUIT:
                    running = False
                
                # # Add a new enemy
                elif event.type == self.ADDENEMY:
                    # Create the new enemy and add it to sprite groups
                    new_enemy = Enemy()
                    self.enemies.add(new_enemy)
                    self.all_sprites.add(new_enemy)
                    
                # # Add a new cloud
                elif event.type == self.ADDCLOUD:
                    # Create the new cloud and add it to sprite groups
                    new_cloud = Cloud()
                    self.clouds.add(new_cloud)
                    self.all_sprites.add(new_cloud)
                
            # Get all the keys currently pressed
            pressed_keys = pygame.key.get_pressed()
            
            # Update the player sprite based on user keypresses
            self.player.update(pressed_keys)
            
            # Update enemy position
            self.enemies.update()
            self.clouds.update()

            # Fill the screen with black
            self.screen.fill((135, 206, 250))
            
            if radar:
                self.update_plane_data()
                self.radar = PlaneRadar(
                    size = RADAR_SIZE,
                    plane_data=self.plane_data
                )
                
                for area in self.radar.radar_areas:
                    area.paint_area(self.enemies)
                    self.screen.blit(area.surface, area.radar_rect)
            
            for entity in self.all_sprites:
                self.screen.blit(entity.surf, entity.rect)
            
            if pygame.sprite.spritecollideany(self.player, self.enemies):
                # If so, then remove the player and stop the loop
                self.player.kill()
                break
            
            # Update the display
            pygame.display.flip()

            # Ensure program maintains a rate of 30 frames per second
            self.clock.tick(SPEED)

if __name__ == "__main__":
    game = FlightGame()
    game.run()