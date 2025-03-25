# Shooter Game

Welcome to **Shooter**, a thrilling two-player competitive game built in Python! In this game, players compete to hit targets within a time limit, earning points based on the distance between their shots. With features like user authentication, game saving/loading, a leaderboard, and customizable settings, it’s an engaging experience for players and a good project for developers to explore.

---

## Features

- **Authentication:** Sign up and log in to track your game history and scores.
- **Game Saving and Loading:** Save your progress and resume your game anytime.
- **Leaderboard:** View the top 5 matches based on highest scores.
- **Customizable Settings:** Adjust sound volume and set custom controls to suit your preferences.
- **Competitive Gameplay:** Compete head-to-head, hitting targets with points awarded for accuracy and distance.

---

## Gameplay Mechanics

The game introduces several interactive features that add strategic depth:

- **Freeze Opponent:** Hitting the snow target temporarily freezes your opponent.
- **Thunder Strike:** Hitting the thunder target grants a number of points.
- **Extra Time:** Hitting the designated target increases the time limit.
- **monster target Distance Consideration:** Players must strategize based on the monster targets position.
- **Extra Bullets:** Hitting a special target grants additional bullets.

---

## Technologies Used

The project is developed using the following technologies:

- **Python:** Core programming language for the game.
- **Pygame:** Library used for game development and rendering.
- **SQLite3:** Lightweight database for storing user data and game history.



---

## Setup and Installation

Follow these steps to get the game running on your machine:

### Prerequisites

- Ensure **Python 3.x** is installed on your system.

### Install Dependencies

Run the following command to install all required dependencies:

```bash
pip install -r requirements.txt
```

### Clone the Repository

```bash
git clone https://github.com/aminfaghih/AP-D3.git
cd AP-D3
```

### Run the Game

```bash
python main.py
```

---

## Project Structure

Here’s an overview of the key files and their purposes:

- **main.py** - The entry point of the game. Manages the main loop and menu navigation.
- **game.py** - Core game logic, including player management, target spawning, and gameplay mechanics.
- **game\_objects.py** - Defines game entities like targets and special items.
- **authentication.py** - Handles user sign-up, login, and session management.
- **settings.py** - Controls game settings like sound volume and key bindings.
- **leaderboard.py** - Displays and updates the leaderboard with top scores.
- **load.py** - Manages saving and loading game states.
- **user.py** - Defines the User class for handling player data.

---

## Assets

The game includes various assets to enhance the experience:

- **Images:** Visuals for targets, special items, and UI elements.
- **Sound Effects:** Audio for shooting, hitting targets, and more.
- **Background Music:** Plays in menus (paused during gameplay).



