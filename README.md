# Naval Newbie

A 2D naval battle game where players control warships, fight progressively stronger enemies, earn coins, and upgrade their ships.

## Installation

Make sure you have **Python 3** installed.

Install the required Python packages:

```bash
pip3 install pyautogui
pip3 install numpy
```

## How to Run

Run the main Python file:

```bash
python3 naval_newbie.py
```

## Game Overview

The game is a warship battle game where the player controls a naval ship using the **keyboard** and aims and fires artillery using the **mouse**.

The game includes an endless **single-player battle mode**, progressively stronger enemies, ship upgrades, projectile-based combat, and an in-game coin system.

## Features

### 1. Game Map

* The game takes place in an ocean environment.
* Islands are placed throughout the ocean.
* Islands are represented using hills made from cones or spheres.
* Ships can only move through water.
* Ships cannot move onto or through islands.
* Shells and torpedoes also collide with islands.

### 2. Player Control

* Ships are controlled using the keyboard.
* Ships have:

  * Acceleration
  * Deceleration
  * Maximum speed
* Turning is only possible while the ship is moving.
* Ships cannot turn in place like a tank.
* The mouse is used to aim the artillery cannons.
* Each artillery cannon has its own range of motion.
* **Left Click** fires artillery shells.
* **Right Click** fires torpedoes.

### 3. Projectile System

* Artillery shells use projectile-based movement.
* Shells take time to reach their targets.
* Players must account for enemy movement when aiming.
* Moving enemies may require the player to lead their shots.
* Torpedoes:

  * Deal high damage.
  * Move slowly.
  * Have a shorter range.
* Shells and torpedoes have individual reload times.
* Weapons cannot be fired until their reload time has completed.

### 4. Ships and Upgrades

The player owns two types of ships:

* **Battleship**

  * Higher hitpoints
  * Higher damage
  * Lower speed
  * Lower fire rate

* **Destroyer**

  * Lower hitpoints
  * Lower damage
  * Higher speed
  * Higher fire rate

Players can spend coins earned from battles to upgrade:

* Damage
* Health Points
* Speed

Each ship has its **own individual upgrades**.

### 5. Single Player Mode

* Single player is an endless battle mode.
* Enemies continuously spawn.
* The game continues until the player's ship is destroyed.
* Enemy strength increases over time.
* Stronger enemies deal more damage.
* Destroying stronger enemies provides greater coin rewards.

### 6. User Interface

The main menu provides options to:

* Start Single Player mode
* Upgrade ships
* Select a ship
* Quit the game

The ship upgrade menu:

* Displays both available ships.
* Allows the player to select a ship.
* Provides an interface for upgrading the selected ship.

During gameplay:

* Press **Escape** to open the pause menu.
* The pause menu allows the player to:

  * Continue playing
  * Return to the main menu

The gameplay HUD displays:

* Crosshair
* Reload status
* Player health bar
* Current coin balance

### 7. Autosave

* Ship upgrades are automatically saved while the game is running.
* The player's coin balance is automatically saved.
* Saved progress is stored in a save file.

## Repository

**GitHub:**
https://github.com/A-N-M-Noor/Naval_Newbie

## Development Updates

### Update 1 — August 18, 2026

What we had completed so far:

https://youtu.be/DRbHMfnBSU8

### Update 2 — August 20, 2026

Latest development progress:

https://youtu.be/w-J7b20a6RI

### Update 3 — August 21, 2026

Latest development progress:

https://youtu.be/HrJicWo0814
