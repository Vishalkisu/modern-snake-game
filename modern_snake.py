import pygame
import random
import sys
import json
import os
import math
from pygame import gfxdraw
import pygame_widgets
from pygame_widgets.button import Button as WidgetButton
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
GRID_SIZE = 25
GRID_WIDTH = (WINDOW_WIDTH - 200) // GRID_SIZE  # Gameplay area width
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Modern Color Palette
COLORS = {
    'background': (18, 18, 18),
    'grid': (30, 30, 30),
    'text': (240, 240, 240),
    'accent1': (75, 139, 190),  # Blue
    'accent2': (255, 89, 94),   # Red
    'accent3': (138, 201, 38),  # Green
    'accent4': (255, 186, 8),   # Yellow
    'panel': (35, 35, 35),
    'button': (45, 45, 45),
    'button_hover': (55, 55, 55),
    'gradient1': (41, 128, 185),  # Blue
    'gradient2': (142, 68, 173),  # Purple
}

# Game settings
DIFFICULTY_SPEEDS = {
    "Beginner": 6,
    "Easy": 8,
    "Medium": 12,
    "Hard": 16,
    "Expert": 20,
    "Master": 25
}

DIFFICULTY_FEATURES = {
    "Beginner": {
        "speed": 6,
        "score_multiplier": 1,
        "grow_amount": 1,
        "wall_collision": False,  # Can pass through walls
        "description": "Perfect for beginners!"
    },
    "Easy": {
        "speed": 8,
        "score_multiplier": 1.2,
        "grow_amount": 1,
        "wall_collision": False,
        "description": "A gentle challenge"
    },
    "Medium": {
        "speed": 12,
        "score_multiplier": 1.5,
        "grow_amount": 1,
        "wall_collision": False,
        "description": "The classic experience"
    },
    "Hard": {
        "speed": 16,
        "score_multiplier": 2,
        "grow_amount": 2,
        "wall_collision": True,  # Die on wall collision
        "description": "For skilled players"
    },
    "Expert": {
        "speed": 20,
        "score_multiplier": 2.5,
        "grow_amount": 2,
        "wall_collision": True,
        "description": "A true challenge"
    },
    "Master": {
        "speed": 25,
        "score_multiplier": 3,
        "grow_amount": 3,
        "wall_collision": True,
        "description": "Only for the best!"
    }
}

class ModernSnake:
    def __init__(self, color):
        self.positions = [(GRID_WIDTH // 4, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False
        self.color = color
        self.length = 1
        self.grow_amount = 1

    def get_head_position(self):
        return self.positions[0]

    def update(self, wall_collision=False):
        current = self.get_head_position()
        x, y = self.direction
        new_x = current[0] + x
        new_y = current[1] + y
        
        # Handle wall collision based on difficulty
        if wall_collision:
            if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
                return False
            new = (new_x, new_y)
        else:
            new = (new_x % GRID_WIDTH, new_y % GRID_HEIGHT)
        
        if new in self.positions[2:]:
            return False
        
        self.positions.insert(0, new)
        if not self.grow:
            self.positions.pop()
        else:
            # Add multiple segments based on grow_amount
            self.grow = False
            self.length += self.grow_amount
        return True

    def render(self, surface):
        for i, p in enumerate(self.positions):
            # Calculate alpha value for gradient effect
            alpha = int(255 * (1 - i / len(self.positions) * 0.5))
            color = list(self.color) + [alpha]
            
            # Draw rounded rectangle for each segment
            x = p[0] * GRID_SIZE + 200  # Offset for sidebar
            y = p[1] * GRID_SIZE
            rect = pygame.Rect(x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
            
            # Draw segment with rounded corners
            pygame.draw.rect(surface, color, rect, border_radius=5)

class ModernFood:
    def __init__(self, color):
        self.position = (0, 0)
        self.color = color
        self.randomize_position()
        self.pulse = 0

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1),
                        random.randint(0, GRID_HEIGHT - 1))

    def render(self, surface):
        # Pulsing animation
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        size = int(GRID_SIZE * (0.6 + math.sin(self.pulse) * 0.1))
        
        x = self.position[0] * GRID_SIZE + 200 + (GRID_SIZE - size) // 2
        y = self.position[1] * GRID_SIZE + (GRID_SIZE - size) // 2
        
        # Draw food with glow effect
        pygame.draw.circle(surface, (*self.color, 100), (x + size//2, y + size//2), size//2 + 4)
        pygame.draw.circle(surface, self.color, (x + size//2, y + size//2), size//2)

class ModernGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Modern Snake")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 100)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 24)
        
        self.state = "menu"
        self.paused = False
        self.current_difficulty = "Medium"
        self.difficulty_info = DIFFICULTY_FEATURES[self.current_difficulty]
        self.setup_buttons()
        self.reset_game()
        
        # Load sounds
        self.load_sounds()
        
        # Load high scores
        self.load_high_scores()
        
        # Menu animations
        self.particles = []
        self.create_particles()
        
        # Demo snake for menu
        self.demo_snake_pos = []
        self.demo_snake_dir = (1, 0)
        self.demo_snake_length = 10
        self.demo_snake_speed = 0.2
        self.demo_snake_last_update = time.time()
        
        # Color animation
        self.color_time = 0
        self.color_speed = 0.001

    def create_particles(self):
        for _ in range(50):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            speed = random.uniform(0.5, 2)
            size = random.randint(2, 5)
            self.particles.append({
                'pos': [x, y],
                'speed': speed,
                'size': size,
                'angle': random.uniform(0, math.pi * 2)
            })

    def update_particles(self):
        for particle in self.particles:
            particle['pos'][0] += math.cos(particle['angle']) * particle['speed']
            particle['pos'][1] += math.sin(particle['angle']) * particle['speed']
            
            # Wrap around screen
            if particle['pos'][0] < 0:
                particle['pos'][0] = WINDOW_WIDTH
            elif particle['pos'][0] > WINDOW_WIDTH:
                particle['pos'][0] = 0
            if particle['pos'][1] < 0:
                particle['pos'][1] = WINDOW_HEIGHT
            elif particle['pos'][1] > WINDOW_HEIGHT:
                particle['pos'][1] = 0

    def draw_particles(self):
        for particle in self.particles:
            alpha = int(128 + 127 * math.sin(time.time() * 2 + particle['pos'][0] * 0.01))
            color = (*COLORS['accent1'][:3], alpha)
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
            self.screen.blit(particle_surface, (particle['pos'][0] - particle['size'], particle['pos'][1] - particle['size']))

    def setup_buttons(self):
        btn_width = 240
        btn_height = 50
        center_x = WINDOW_WIDTH // 2 - btn_width // 2
        start_y = WINDOW_HEIGHT // 2 + 30
        spacing = 70

        self.buttons = {
            'start': WidgetButton(
                self.screen, center_x, start_y, btn_width, btn_height,
                text='Start Game',
                fontSize=28,
                margin=20,
                inactiveColour=(*COLORS['button'][:3], 200),
                hoverColour=COLORS['button_hover'],
                pressedColour=COLORS['accent1'],
                radius=25,
                onClick=lambda: setattr(self, 'state', 'game')
            ),
            'difficulty': WidgetButton(
                self.screen, center_x, start_y + spacing, btn_width, btn_height,
                text=f'Difficulty: {self.current_difficulty}',
                fontSize=28,
                margin=20,
                inactiveColour=(*COLORS['button'][:3], 200),
                hoverColour=COLORS['button_hover'],
                pressedColour=COLORS['accent1'],
                radius=25
            )
        }

    def draw_menu(self):
        # Draw animated background
        self.update_particles()
        self.draw_particles()
        
        # Update color animation
        self.color_time += self.color_speed
        glow_color = (
            int(127 + 127 * math.sin(self.color_time)),
            int(127 + 127 * math.sin(self.color_time + 2)),
            int(127 + 127 * math.sin(self.color_time + 4))
        )
        
        # Draw title with glow effect
        title_text = "SNAKE"
        wave_offset = math.sin(time.time() * 2) * 10
        
        # Draw glow
        for offset in range(10, 0, -2):
            glow_surface = self.title_font.render(title_text, True, (*glow_color, 25))
            glow_pos = (WINDOW_WIDTH//2 - glow_surface.get_width()//2 + offset,
                       WINDOW_HEIGHT//4 - glow_surface.get_height()//2 + wave_offset + offset)
            self.screen.blit(glow_surface, glow_pos)
        
        # Draw main title
        title = self.title_font.render(title_text, True, COLORS['text'])
        title_pos = (WINDOW_WIDTH//2 - title.get_width()//2,
                    WINDOW_HEIGHT//4 - title.get_height()//2 + wave_offset)
        self.screen.blit(title, title_pos)
        
        # Draw subtitle with fade effect
        alpha = int(128 + 127 * math.sin(time.time() * 2))
        subtitle_surface = pygame.Surface((400, 40), pygame.SRCALPHA)
        subtitle = self.subtitle_font.render('Use arrow keys to control', True, (*COLORS['accent1'][:3], alpha))
        subtitle_pos = (200 - subtitle.get_width()//2, 0)
        subtitle_surface.blit(subtitle, subtitle_pos)
        self.screen.blit(subtitle_surface, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//4 + 60))
        
        # Draw difficulty description with fade effect
        desc_surface = pygame.Surface((400, 40), pygame.SRCALPHA)
        desc = self.subtitle_font.render(self.difficulty_info["description"], True, (*COLORS['accent4'][:3], alpha))
        desc_pos = (200 - desc.get_width()//2, 0)
        desc_surface.blit(desc, desc_pos)
        self.screen.blit(desc_surface, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT - 60))
        
        # Draw high scores panel
        self.draw_high_scores_panel()

    def draw_high_scores_panel(self):
        panel_width = 300
        panel_height = 200
        panel_x = WINDOW_WIDTH - panel_width - 20
        panel_y = 20
        
        # Create panel surface with transparency
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*COLORS['panel'][:3], 200), (0, 0, panel_width, panel_height), border_radius=15)
        
        # Draw title
        title = self.subtitle_font.render('High Scores', True, COLORS['text'])
        panel.blit(title, (panel_width//2 - title.get_width()//2, 10))
        
        # Draw scores
        y_offset = 50
        for difficulty, score in self.high_scores.items():
            # Create gradient color based on difficulty
            color_index = list(DIFFICULTY_FEATURES.keys()).index(difficulty)
            color_ratio = color_index / (len(DIFFICULTY_FEATURES) - 1)
            color = (
                int(255 * (1 - color_ratio)),
                int(255 * color_ratio),
                int(128 + 127 * math.sin(time.time() + color_index))
            )
            
            text = self.info_font.render(f'{difficulty}: {score}', True, color)
            panel.blit(text, (20, y_offset))
            y_offset += 25
        
        self.screen.blit(panel, (panel_x, panel_y))

    def load_high_scores(self):
        try:
            with open("high_scores.json", 'r') as f:
                self.high_scores = json.load(f)
                # Ensure all difficulties exist in high scores
                for difficulty in DIFFICULTY_FEATURES.keys():
                    if difficulty not in self.high_scores:
                        self.high_scores[difficulty] = 0
        except:
            # Initialize high scores for all difficulties
            self.high_scores = {diff: 0 for diff in DIFFICULTY_FEATURES.keys()}
            self.save_high_scores()

    def save_high_scores(self):
        with open("high_scores.json", 'w') as f:
            json.dump(self.high_scores, f)

    def load_sounds(self):
        self.sounds = {
            "eat": pygame.mixer.Sound("sounds/eat.wav") if os.path.exists("sounds/eat.wav") else None,
            "crash": pygame.mixer.Sound("sounds/crash.wav") if os.path.exists("sounds/crash.wav") else None
        }

    def reset_game(self):
        self.snake = ModernSnake(COLORS['accent3'])
        self.food = ModernFood(COLORS['accent2'])
        self.score = 0
        self.game_over = False
        self.difficulty_info = DIFFICULTY_FEATURES[self.current_difficulty]
        self.snake.grow_amount = self.difficulty_info["grow_amount"]

    def return_to_menu(self):
        self.state = "menu"
        self.paused = False
        self.reset_game()

    def draw_sidebar(self):
        # Draw sidebar background
        sidebar = pygame.Surface((200, WINDOW_HEIGHT))
        sidebar.fill(COLORS['panel'])
        self.screen.blit(sidebar, (0, 0))

        # Draw score
        score_text = self.info_font.render(f'Score: {self.score}', True, COLORS['text'])
        self.screen.blit(score_text, (20, 20))

        # Draw high score
        high_score = self.high_scores[self.current_difficulty]
        high_score_text = self.info_font.render(f'Best: {high_score}', True, COLORS['text'])
        self.screen.blit(high_score_text, (20, 60))

        # Draw difficulty
        diff_text = self.info_font.render(self.current_difficulty, True, COLORS['accent1'])
        self.screen.blit(diff_text, (20, 100))

        # Draw ESC key hint
        esc_text = self.info_font.render('ESC - Back to Menu', True, COLORS['accent4'])
        self.screen.blit(esc_text, (20, WINDOW_HEIGHT - 40))

    def draw_grid(self):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(x * GRID_SIZE + 200, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, COLORS['grid'], rect, 1)

    def draw_pause_screen(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(COLORS['background'])
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))

        # Draw pause text
        pause_text = self.title_font.render('PAUSED', True, COLORS['text'])
        self.screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//3))

        # Draw instructions
        text_color = COLORS['accent1']
        y_pos = WINDOW_HEIGHT//2
        spacing = 40

        instructions = [
            ('ESC', 'Return to Menu'),
            ('SPACE', 'Resume Game')
        ]

        for key, action in instructions:
            key_text = self.subtitle_font.render(key, True, text_color)
            action_text = self.subtitle_font.render(action, True, COLORS['text'])
            
            # Center both texts
            total_width = key_text.get_width() + 20 + action_text.get_width()
            start_x = WINDOW_WIDTH//2 - total_width//2
            
            self.screen.blit(key_text, (start_x, y_pos))
            self.screen.blit(action_text, (start_x + key_text.get_width() + 20, y_pos))
            y_pos += spacing

    def run(self):
        while True:
            self.screen.fill(COLORS['background'])
            events = pygame.event.get()
            
            # Handle events
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if self.state == "game":
                        if event.key == pygame.K_ESCAPE:
                            self.return_to_menu()
                            continue
                        elif event.key == pygame.K_SPACE and self.paused:
                            self.paused = False
                            continue
                        elif not self.paused:
                            if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                                self.snake.direction = (0, -1)
                            elif event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                                self.snake.direction = (0, 1)
                            elif event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                                self.snake.direction = (-1, 0)
                            elif event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                                self.snake.direction = (1, 0)
                    elif self.state == "game_over" and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.return_to_menu()
                    elif self.paused:
                        if event.key == pygame.K_ESCAPE:
                            self.return_to_menu()
                            self.paused = False
            
            # Update buttons only in menu state
            if self.state == "menu":
                pygame_widgets.update(events)
                for button in self.buttons.values():
                    button.show()
                if self.buttons['start'].clicked:
                    self.state = "game"
                    self.reset_game()
                elif self.buttons['difficulty'].clicked:
                    difficulties = list(DIFFICULTY_FEATURES.keys())
                    current_index = difficulties.index(self.current_difficulty)
                    self.current_difficulty = difficulties[(current_index + 1) % len(difficulties)]
                    self.difficulty_info = DIFFICULTY_FEATURES[self.current_difficulty]
                    # Update button text
                    self.buttons['difficulty'] = WidgetButton(
                        self.screen, 
                        self.buttons['difficulty'].getX(),
                        self.buttons['difficulty'].getY(),
                        self.buttons['difficulty'].getWidth(),
                        self.buttons['difficulty'].getHeight(),
                        text=f'Difficulty: {self.current_difficulty}',
                        fontSize=28,
                        margin=20,
                        inactiveColour=(*COLORS['button'][:3], 200),
                        hoverColour=COLORS['button_hover'],
                        pressedColour=COLORS['accent1'],
                        radius=25
                    )
            else:
                for button in self.buttons.values():
                    button.hide()
            
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game":
                self.draw_grid()
                self.draw_sidebar()
                
                if not self.game_over and not self.paused:
                    if not self.snake.update(self.difficulty_info["wall_collision"]):
                        if self.sounds["crash"]:
                            self.sounds["crash"].play()
                        if self.score > self.high_scores[self.current_difficulty]:
                            self.high_scores[self.current_difficulty] = self.score
                            self.save_high_scores()
                        self.game_over = True

                    if self.snake.get_head_position() == self.food.position:
                        if self.sounds["eat"]:
                            self.sounds["eat"].play()
                        self.snake.grow = True
                        self.food.randomize_position()
                        self.score += int(10 * self.difficulty_info["score_multiplier"])

                self.snake.render(self.screen)
                self.food.render(self.screen)

                if self.paused:
                    self.draw_pause_screen()

            elif self.state == "game_over":
                # Draw game over screen
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.fill(COLORS['background'])
                overlay.set_alpha(200)
                self.screen.blit(overlay, (0, 0))

                game_over = self.title_font.render('GAME OVER', True, COLORS['accent2'])
                score_text = self.info_font.render(f'Final Score: {self.score}', True, COLORS['text'])
                continue_text = self.info_font.render('Press ENTER to continue', True, COLORS['accent1'])
                
                self.screen.blit(game_over, (WINDOW_WIDTH//2 - game_over.get_width()//2, WINDOW_HEIGHT//2 - 100))
                self.screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2))
                self.screen.blit(continue_text, (WINDOW_WIDTH//2 - continue_text.get_width()//2, WINDOW_HEIGHT//2 + 100))

            pygame.display.flip()
            self.clock.tick(DIFFICULTY_FEATURES[self.current_difficulty]["speed"])

if __name__ == '__main__':
    game = ModernGame()
    game.run()
