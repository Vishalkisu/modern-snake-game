import pygame
import random
import sys
import json
from pathlib import Path
import os

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Game settings
DIFFICULTY_SPEEDS = {
    "Easy": 10,
    "Medium": 15,
    "Hard": 20
}

# Color themes
COLOR_THEMES = {
    "Classic": {"snake": GREEN, "food": RED, "background": BLACK},
    "Ocean": {"snake": BLUE, "food": YELLOW, "background": (0, 100, 200)},
    "Forest": {"snake": (34, 139, 34), "food": (139, 69, 19), "background": (0, 100, 0)},
}

class Snake:
    def __init__(self, color):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False
        self.color = color

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        current = self.get_head_position()
        x, y = self.direction
        new = ((current[0] + x) % GRID_WIDTH, (current[1] + y) % GRID_HEIGHT)
        
        if new in self.positions[2:]:
            return False
        
        self.positions.insert(0, new)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        return True

    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False

    def render(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, self.color, 
                           (p[0] * GRID_SIZE, p[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Food:
    def __init__(self, color):
        self.position = (0, 0)
        self.color = color
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1),
                        random.randint(0, GRID_HEIGHT - 1))

    def render(self, surface):
        pygame.draw.rect(surface, self.color,
                        (self.position[0] * GRID_SIZE, 
                         self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Enhanced Snake Game')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Load high scores
        self.high_scores_file = "high_scores.json"
        self.load_high_scores()
        
        # Load sounds
        self.load_sounds()
        
        # Game state
        self.state = "menu"  # menu, game, game_over
        self.current_difficulty = "Medium"
        self.current_theme = "Classic"
        
        # Create buttons
        self.create_buttons()
        
        self.reset_game()

    def load_sounds(self):
        # Create sounds directory if it doesn't exist
        sounds_dir = Path("sounds")
        sounds_dir.mkdir(exist_ok=True)
        
        # Initialize sound effects (you'll need to provide actual sound files)
        self.sounds = {
            "eat": pygame.mixer.Sound("sounds/eat.wav") if os.path.exists("sounds/eat.wav") else None,
            "crash": pygame.mixer.Sound("sounds/crash.wav") if os.path.exists("sounds/crash.wav") else None
        }

    def create_buttons(self):
        self.menu_buttons = {
            "start": Button(300, 200, 200, 50, "Start Game", GREEN),
            "difficulty": Button(300, 270, 200, 50, f"Difficulty: {self.current_difficulty}", BLUE),
            "theme": Button(300, 340, 200, 50, f"Theme: {self.current_theme}", PURPLE)
        }

    def load_high_scores(self):
        try:
            with open(self.high_scores_file, 'r') as f:
                self.high_scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.high_scores = {"Easy": 0, "Medium": 0, "Hard": 0}

    def save_high_scores(self):
        with open(self.high_scores_file, 'w') as f:
            json.dump(self.high_scores, f)

    def reset_game(self):
        theme = COLOR_THEMES[self.current_theme]
        self.snake = Snake(theme["snake"])
        self.food = Food(theme["food"])
        self.score = 0
        self.background_color = theme["background"]

    def handle_menu_click(self, pos):
        if self.menu_buttons["start"].is_clicked(pos):
            self.state = "game"
        elif self.menu_buttons["difficulty"].is_clicked(pos):
            difficulties = list(DIFFICULTY_SPEEDS.keys())
            current_index = difficulties.index(self.current_difficulty)
            self.current_difficulty = difficulties[(current_index + 1) % len(difficulties)]
            self.menu_buttons["difficulty"].text = f"Difficulty: {self.current_difficulty}"
        elif self.menu_buttons["theme"].is_clicked(pos):
            themes = list(COLOR_THEMES.keys())
            current_index = themes.index(self.current_theme)
            self.current_theme = themes[(current_index + 1) % len(themes)]
            self.menu_buttons["theme"].text = f"Theme: {self.current_theme}"
            self.reset_game()

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "menu":
                self.handle_menu_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if self.state == "game":
                    if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                        self.snake.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                        self.snake.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                        self.snake.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                        self.snake.direction = (1, 0)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                elif self.state == "game_over" and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.state = "menu"

    def draw_menu(self):
        self.screen.fill(BLACK)
        for button in self.menu_buttons.values():
            button.draw(self.screen)
        
        # Draw high scores
        y_offset = 420
        title = self.font.render("High Scores:", True, WHITE)
        self.screen.blit(title, (300, y_offset))
        
        for difficulty, score in self.high_scores.items():
            y_offset += 40
            score_text = self.font.render(f"{difficulty}: {score}", True, WHITE)
            self.screen.blit(score_text, (300, y_offset))

    def draw_game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.font.render("Game Over!", True, WHITE)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        continue_text = self.font.render("Press ENTER to continue", True, WHITE)
        
        self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2))
        self.screen.blit(continue_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 50))

    def run(self):
        while True:
            self.handle_keys()
            
            if self.state == "menu":
                self.draw_menu()
            
            elif self.state == "game":
                # Update snake position
                if not self.snake.update():
                    if self.sounds["crash"]:
                        self.sounds["crash"].play()
                    if self.score > self.high_scores[self.current_difficulty]:
                        self.high_scores[self.current_difficulty] = self.score
                        self.save_high_scores()
                    self.state = "game_over"
                    continue

                # Check for food collision
                if self.snake.get_head_position() == self.food.position:
                    if self.sounds["eat"]:
                        self.sounds["eat"].play()
                    self.snake.grow = True
                    self.food.randomize_position()
                    self.score += 1

                # Draw everything
                self.screen.fill(self.background_color)
                self.snake.render(self.screen)
                self.food.render(self.screen)
                
                # Draw score
                score_text = self.font.render(f'Score: {self.score}', True, WHITE)
                self.screen.blit(score_text, (10, 10))
                
                # Draw current difficulty
                diff_text = self.font.render(f'Difficulty: {self.current_difficulty}', True, WHITE)
                self.screen.blit(diff_text, (10, 40))
                
                self.clock.tick(DIFFICULTY_SPEEDS[self.current_difficulty])
            
            elif self.state == "game_over":
                self.draw_game_over()
            
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()
