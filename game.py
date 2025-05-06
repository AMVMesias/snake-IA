import pygame
import random
import math
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
LIGHT_RED = (255, 100, 100)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
DARK_BLUE = (0, 0, 150)
BLACK = (0, 0, 0)
GRID_COLOR = (20, 20, 20)
GLOW_COLOR = (255, 255, 200)

BLOCK_SIZE = 20
SPEED = 40

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake AI')
        self.clock = pygame.time.Clock()
        # Create surfaces for effects
        self.background = pygame.Surface((self.w, self.h))
        self.draw_background_grid()
        self.time = 0
        self.reset()

    def draw_background_grid(self):
        # Draw a subtle grid pattern in the background
        self.background.fill(BLACK)
        for x in range(0, self.w, BLOCK_SIZE):
            pygame.draw.line(self.background, GRID_COLOR, (x, 0), (x, self.h))
        for y in range(0, self.h, BLOCK_SIZE):
            pygame.draw.line(self.background, GRID_COLOR, (0, y), (self.w, y))

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        self.time = 0

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        self.time += 0.1  # Increment time for animations
        
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        # Blit the background with grid
        self.display.blit(self.background, (0, 0))
        
        # Draw snake with gradient effect
        for i, pt in enumerate(self.snake):
            # Calculate color intensity based on position in snake
            intensity = 1 - (i / (len(self.snake) * 1.5))
            if intensity < 0.3:
                intensity = 0.3
                
            # Create gradient color
            color = (int(BLUE1[0] * intensity), int(BLUE1[1] * intensity), int(255 * intensity))
            inner_color = (int(BLUE2[0] * intensity), int(BLUE2[1] * intensity), int(255 * intensity))
            
            # Draw snake segment with rounded corners
            pygame.draw.rect(self.display, color, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE), border_radius=3)
            pygame.draw.rect(self.display, inner_color, pygame.Rect(pt.x+4, pt.y+4, 12, 12), border_radius=2)
            
            # Add highlight to head
            if i == 0:
                # Draw eyes
                eye_radius = 2
                eye_offset_x = 5
                eye_offset_y = 8
                
                if self.direction == Direction.RIGHT:
                    pygame.draw.circle(self.display, WHITE, (pt.x + BLOCK_SIZE - eye_offset_x, pt.y + eye_offset_y), eye_radius)
                    pygame.draw.circle(self.display, WHITE, (pt.x + BLOCK_SIZE - eye_offset_x, pt.y + BLOCK_SIZE - eye_offset_y), eye_radius)
                elif self.direction == Direction.LEFT:
                    pygame.draw.circle(self.display, WHITE, (pt.x + eye_offset_x, pt.y + eye_offset_y), eye_radius)
                    pygame.draw.circle(self.display, WHITE, (pt.x + eye_offset_x, pt.y + BLOCK_SIZE - eye_offset_y), eye_radius)
                elif self.direction == Direction.UP:
                    pygame.draw.circle(self.display, WHITE, (pt.x + eye_offset_y, pt.y + eye_offset_x), eye_radius)
                    pygame.draw.circle(self.display, WHITE, (pt.x + BLOCK_SIZE - eye_offset_y, pt.y + eye_offset_x), eye_radius)
                elif self.direction == Direction.DOWN:
                    pygame.draw.circle(self.display, WHITE, (pt.x + eye_offset_y, pt.y + BLOCK_SIZE - eye_offset_x), eye_radius)
                    pygame.draw.circle(self.display, WHITE, (pt.x + BLOCK_SIZE - eye_offset_y, pt.y + BLOCK_SIZE - eye_offset_x), eye_radius)

        # Draw food with pulsing effect
        pulse = (math.sin(self.time * 5) + 1) / 4 + 0.75  # Value between 0.75 and 1.25
        food_color = (int(RED[0] * pulse), int(RED[1] * pulse), int(RED[2] * pulse))
        
        # Draw food with glow effect
        glow_radius = int(BLOCK_SIZE * (1 + 0.3 * math.sin(self.time * 3)))
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*LIGHT_RED, 40), (glow_radius, glow_radius), glow_radius)
        self.display.blit(glow_surf, (self.food.x + BLOCK_SIZE//2 - glow_radius, self.food.y + BLOCK_SIZE//2 - glow_radius))
        
        # Draw actual food
        pygame.draw.rect(self.display, food_color, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE), border_radius=BLOCK_SIZE//2)
        pygame.draw.rect(self.display, LIGHT_RED, pygame.Rect(self.food.x+2, self.food.y+2, BLOCK_SIZE-4, BLOCK_SIZE-4), border_radius=BLOCK_SIZE//2-1)
        
        # Add a highlight to the food
        highlight_pos = (self.food.x + 5, self.food.y + 5)
        highlight_size = 3
        pygame.draw.circle(self.display, WHITE, highlight_pos, highlight_size)

        # Score with shadow effect
        score_text = f"Score: {self.score}"
        text_shadow = font.render(score_text, True, (50, 50, 50))
        text = font.render(score_text, True, WHITE)
        
        # Draw text with shadow
        self.display.blit(text_shadow, [2, 2])
        self.display.blit(text, [0, 0])
        
        pygame.display.flip()

    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)