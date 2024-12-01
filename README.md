# Modern Snake Game

A modern implementation of the classic Snake game using Python and Pygame, featuring multiple difficulty levels, high scores, and beautiful visual effects.

## Features

- 6 Difficulty Levels: Beginner, Easy, Medium, Hard, Expert, Master
- Modern UI with particle effects and animations
- High score tracking for each difficulty level
- Dynamic color effects and transitions
- Sound effects for enhanced gameplay
- Pause functionality with ESC key
- Smooth snake movement and controls

## Requirements

- Python 3.x
- Pygame 2.5.2
- pygame-widgets 1.1.1

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/modern-snake-game.git
cd modern-snake-game
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python modern_snake.py
```

2. Controls:
- Arrow keys: Control snake direction
- ESC: Return to menu
- SPACE: Resume game when paused
- ENTER/SPACE: Restart after game over

3. Difficulty Levels:
- Beginner: Slow speed, no wall collision
- Easy: Moderate speed, no wall collision
- Medium: Classic experience
- Hard: Fast speed, wall collision enabled
- Expert: Very fast, increased growth
- Master: Ultimate challenge

## Project Structure

- `modern_snake.py`: Main game implementation
- `requirements.txt`: Python dependencies
- `high_scores.json`: Persistent high score storage
- `sounds/`: Directory containing game sound effects

## Credits

Created by [Your Name]
