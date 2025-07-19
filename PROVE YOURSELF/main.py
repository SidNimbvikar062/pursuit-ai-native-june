import pygame
import sys
import random
import json
import os
import socket # NEW: For internet connectivity check
import google.generativeai as genai # NEW: For Gemini AI
from character import Character
from move import Move
from button import Button

# --- Initialization ---
os.environ['GEMINI_API_KEY'] = "AIzaSyBOzuqTZYT-cMFSc4jW9XfAZiKLizJPrKQ"
pygame.init()
pygame.mixer.init() # Initialize the mixer for music

# --- Screen Dimensions ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# --- GAME TITLE ---
GAME_TITLE = "PROVE YOURSELF"
pygame.display.set_caption(GAME_TITLE)

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (50, 50, 50)
GREEN = (0, 200, 0)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0) # For warning messages

# --- Fonts ---
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 36)
font_tiny = pygame.font.Font(None, 24)

# --- Game States ---
TITLE_SCREEN = 0
COMBAT_SCREEN = 1
GAME_OVER_SCREEN = 2
GAME_WIN_SCREEN = 3
LEVEL_UP_SCREEN = 4
current_game_state = TITLE_SCREEN

# --- Combat Sub-States ---
PLAYER_CHOOSING_ACTION = 0
PLAYER_CHOOSING_WEAPON_MOVE = 1
PLAYER_CHOOSING_MAGIC_MOVE = 2
PROCESSING_TURN = 3
WAITING_FOR_PLAYER_INPUT_TO_PROGRESS = 4
current_combat_sub_state = PLAYER_CHOOSING_ACTION

displaying_stats = False

# --- Battle Log / Message System ---
battle_message_queue = []
current_display_message = {"text": "", "color": WHITE}

# --- Global Game Data (loaded from JSON) ---
all_moves = {} # This holds 'Move' objects
all_moves_json_data = {} # NEW: This holds the raw dictionary data from moves.json, needed for AI prompt
enemy_templates = {}
image_cache = {} # Global cache for loaded images

# --- Music File Paths ---
script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, "data")
music_dir = os.path.join(data_dir, "music") # Ensure this path is correct

COMBAT_MUSIC_PATH = os.path.join(music_dir, "combat_loop.ogg") # Make sure you have this file
LEVEL_UP_MUSIC_PATH = os.path.join(music_dir, "level_up_fanfare.ogg") # Make sure you have this file

# --- Global Music Control Flags/Variables ---
current_music_playing = None # To keep track of what's playing

# --- Gemini AI Configuration ---
# IMPORTANT: Store your API key as an environment variable named GEMINI_API_KEY
# e.g., in your terminal before running: export GEMINI_API_KEY="YOUR_API_KEY_HERE"
# On Windows PowerShell: $env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY environment variable not set. Gemini AI will be unavailable. Please set it to use Realistic AI mode.")

IS_GEMINI_AVAILABLE = False # Global flag for API availability, updated at startup/selection
AI_MODE = "Random" # Global variable to store selected AI mode ("Random" or "Realistic")

# --- Image loading function with caching ---
def load_image_with_cache(image_path, size=None):
    """Loads an image from a path, caches it, and scales it if a size is provided."""
    cache_key = (image_path, size)
    if cache_key in image_cache:
        return image_cache[cache_key]

    full_path = os.path.join(script_dir, image_path)

    try:
        image = pygame.image.load(full_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        image_cache[cache_key] = image
        return image
    except pygame.error as e:
        print(f"FATAL ERROR: Could not load image from {full_path}. Error: {e}. Returning placeholder.")
        placeholder = pygame.Surface((150, 150), pygame.SRCALPHA)
        placeholder.fill((255, 0, 255))
        return placeholder

# --- Load Moves from JSON ---
def load_moves_from_file():
    global all_moves, all_moves_json_data # NEW: Reference all_moves_json_data
    moves_file_path = os.path.join(data_dir, "moves.json")
    print(f"DEBUG: Attempting to load moves data from {moves_file_path}...")
    try:
        with open(moves_file_path, 'r') as f:
            raw_moves_data = json.load(f) # Load raw data first
            all_moves_json_data = {move['name']: move for move in raw_moves_data} # Store raw data keyed by name
            
            # Now populate all_moves with Move objects
            for move_data in raw_moves_data:
                move = Move(
                    move_data["name"],
                    move_data["accuracy"],
                    tuple(move_data["damage_range"]),
                    move_data["type"],
                    move_data["cost"],
                    move_data.get("speed", 99),
                    status_effect_data=move_data.get("status_effect_data"),
                    heal_range=move_data.get("heal_range"),
                    target=move_data.get("target", "enemy")
                )
                all_moves[move.name] = move
        print(f"DEBUG: Moves loaded")
        print(f"DEBUG: Raw moves data for AI loaded: {list(all_moves_json_data.keys())}")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"FATAL ERROR loading moves: {e}")
        sys.exit()

# --- Load Enemy Templates from JSON ---
def load_enemy_templates_from_file():
    global enemy_templates
    enemies_file_path = os.path.join(data_dir, "enemies.json")
    print(f"DEBUG: Attempting to load enemy data from {enemies_file_path}...")
    try:
        with open(enemies_file_path, 'r') as f:
            enemies_data = json.load(f)
        for enemy_data in enemies_data:
            enemy_templates[enemy_data["name"]] = enemy_data
        print(f"DEBUG: Enemy templates loaded: {list(enemy_templates.keys())}")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"FATAL ERROR loading enemy templates: {e}")
        sys.exit()

# --- Call new separate loading functions ---
load_moves_from_file()
load_enemy_templates_from_file()

# --- NEW: Internet Connectivity Check ---
def check_internet_connectivity(timeout=2):
    """
    Checks for internet connectivity by trying to connect to a well-known server.
    Updates the global IS_GEMINI_AVAILABLE flag.
    """
    global IS_GEMINI_AVAILABLE
    if not GEMINI_API_KEY: # If no API key, Gemini is definitely not available
        IS_GEMINI_AVAILABLE = False
        print("INFO: Gemini API key not set, Realistic AI will be unavailable.")
        return False
    try:
        # Try to connect to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        IS_GEMINI_AVAILABLE = True
        print("INFO: Internet connectivity detected. Gemini AI is available.")
        return True
    except OSError:
        IS_GEMINI_AVAILABLE = False
        print("WARNING: No internet connectivity. Gemini AI will be unavailable.")
        return False
    except Exception as e:
        IS_GEMINI_AVAILABLE = False
        print(f"ERROR: An unexpected error occurred during connectivity check: {e}. Gemini AI will be unavailable.")
        return False

# --- NEW: Gemini AI Move Selection Function ---
# --- NEW: Gemini AI Move Selection Function ---
def choose_ai_move(enemy_char, player_char, all_moves_json_data):
    """
    Uses Gemini API to choose an intelligent move for the enemy.
    Includes persona, detailed battle context, and specific instructions for the AI.
    Handles no-repeat move logic and critical hit overrides.
    """
    model = genai.GenerativeModel('gemini-2.0-flash')

    # --- 1. Construct Persona ---
    # --- 1. Construct Persona ---
    persona = ""
    if enemy_char.name == "Fire Elemental":
        persona = "You are a destructive fire elemental, preferring to burn enemies over time and unleash powerful magical attacks. Your intelligence guides your fiery wrath."
    elif enemy_char.name == "Ice Elemental":
        persona = "You are a resilient ice elemental, focused on enduring attacks, slowing foes, and inflicting chilling damage over time. Your cold logic dictates your actions."
    elif enemy_char.name == "Ogre":
        persona = "You are a brutish, simple-minded ogre, relying on raw strength and debilitating ground attacks. You favor direct confrontation."
    elif enemy_char.name == "Troll":
        persona = "You are a lumbering troll, tough and regenerative. You prioritize outlasting your opponent and crushing them with sheer force."
    elif enemy_char.name == "Goblin":
        persona = "You are a cunning but cowardly goblin, preferring quick strikes and evasive maneuvers. You are not above fleeing if gravely wounded."
    elif enemy_char.name == "Orc":
        persona = "You are a brutal orc warrior, favoring direct, heavy attacks to overpower your foes. You charge into battle without hesitation."
    elif enemy_char.name == "Kobold":
        persona = "You are a small but surprisingly agile kobold, using a mix of quick physical attacks and minor magical bursts. You are opportunistic."
    elif enemy_char.name == "Giant Rat":
        persona = "You are a rabid giant rat, relying on speed and sharp bites to overwhelm smaller prey. You attack relentlessly until your opponent falls."
    elif enemy_char.name == "Slime":
        persona = "You are an amorphous slime, using your corrosive properties to slowly melt away defenses and inflict damage over time. You are resilient."
    elif enemy_char.name == "Dire Wolf":
        persona = "You are a ferocious dire wolf, focusing on swift lunges and tearing attacks to bring down your prey quickly. You are a relentless hunter."
    elif enemy_char.name == "Skeleton":
        persona = "You are an unfeeling skeleton warrior, relentlessly attacking with your bone weapons until your foe is destroyed. You feel no pain or fear."
    elif enemy_char.name == "Zombie":
        persona = "You are a shambling zombie, slow but incredibly tough, relying on decaying touch and bites to spread rot. You prioritize outlasting your opponent."
    elif enemy_char.name == "Giant Spider":
        persona = "You are a predatory giant spider, using webs to entangle and poison to debilitate your prey before closing in for the kill. You are patient and strategic."
    elif enemy_char.name == "Goblin Shaman":
        persona = "You are a mischievous goblin shaman, preferring to weaken enemies with curses and poison before unleashing minor magical attacks. You avoid direct confrontation."
    elif enemy_char.name == "Gnoll":
        persona = "You are a savage gnoll, using brute force and infectious bites to overwhelm your opponents. You are relentless and aggressive."
    elif enemy_char.name == "Bandit":
        persona = "You are a cunning bandit, using a mix of swift blade attacks and surprising shadow magic to take down your targets. You are agile and opportunistic."
    elif enemy_char.name == "Golem":
        persona = "You are a stoic golem, incredibly tough and resilient, relying on powerful, slow physical attacks and endurance. You are difficult to destroy."
    elif enemy_char.name == "Gargoyle":
        persona = "You are a watchful gargoyle, using stone-based magic and curses from a distance. You are methodical in your attacks."
    elif enemy_char.name == "Banshee":
        persona = "You are a spectral banshee, specializing in debilitating screams and curses that weaken the enemy's resolve and defenses. You avoid physical engagement."
    else:
        # Default persona if no specific one is found
        persona = f"You are a fierce {enemy_char.name}, an intelligent creature of this world. Your goal is to defeat the player efficiently."

    # --- 2. Format Available Moves for Prompt ---
    available_moves_for_prompt = []
    # Iterate over the Move objects currently equipped by the enemy
    for move_name, move_obj in enemy_char.moves.items():
        # IMPORTANT: Only include moves the enemy can actually afford MP-wise
        if enemy_char.current_mp < move_obj.cost:
            continue

        # Get the raw data from all_moves_json_data for full details
        full_move_data = all_moves_json_data.get(move_name)
        if not full_move_data:
            print(f"WARNING: Raw data for move '{move_name}' not found in all_moves_json_data. Skipping in AI prompt.")
            continue

        move_str = f"'{move_name}' (Cost: {full_move_data.get('cost', 0)} MP, Type: {full_move_data.get('type', 'unknown')}"
        if 'damage_range' in full_move_data and full_move_data['damage_range'] != [0,0]:
            move_str += f", Damage: {full_move_data['damage_range'][0]}-{full_move_data['damage_range'][1]}"
        if 'heal_range' in full_move_data and full_move_data['heal_range'] != [0,0]:
            move_str += f", Heal: {full_move_data['heal_range'][0]}-{full_move_data['heal_range'][1]}"
        
        # Add detailed status effect info
        if 'status_effect_data' in full_move_data and full_move_data['status_effect_data']:
            effect_name = full_move_data['status_effect_data']['name']
            effect_type = full_move_data['status_effect_data'].get('effect_type', 'unknown')
            duration = full_move_data['status_effect_data'].get('duration', 'N/A')
            move_str += f", Effect: {effect_name} (Type: {effect_type}, Duration: {duration}"
            if effect_type == 'dot':
                dot_dmg = full_move_data['status_effect_data'].get('damage_per_turn', [0,0])
                move_str += f", DOT: {dot_dmg[0]}-{dot_dmg[1]}/turn"
            elif full_move_data['status_effect_data'].get('stat_modifier'):
                mods = ', '.join([f"{k}: {v}" for k, v in full_move_data['status_effect_data']['stat_modifier'].items()])
                move_str += f", Stat Mods: {mods}"
            move_str += ")"
        move_str += f", Description: {full_move_data.get('description', 'No description')})"
        available_moves_for_prompt.append(move_str)

    # --- 3. Format Active Status Effects for Prompt ---
    enemy_effects = []
    for e in enemy_char.active_status_effects:
        effect_desc = f"{e['name']} (Duration: {e['duration']} turns remaining"
        if e.get('effect_type') == 'dot' and 'damage_per_turn' in e:
            dot_dmg = e['damage_per_turn']
            effect_desc += f", DOT: {dot_dmg[0]}-{dot_dmg[1]}/turn"
        elif e.get('stat_modifier'):
            mods = ', '.join([f"{k}: {v}" for k, v in e['stat_modifier'].items()])
            effect_desc += f", Stats: {mods}"
        effect_desc += ")"
        enemy_effects.append(effect_desc)

    player_effects = []
    for e in player_char.active_status_effects:
        effect_desc = f"{e['name']} (Duration: {e['duration']} turns remaining"
        if e.get('effect_type') == 'dot' and 'damage_per_turn' in e:
            dot_dmg = e['damage_per_turn']
            effect_desc += f", DOT: {dot_dmg[0]}-{dot_dmg[1]}/turn"
        elif e.get('stat_modifier'):
            mods = ', '.join([f"{k}: {v}" for k, v in e['stat_modifier'].items()])
            effect_desc += f", Stats: {mods}"
        effect_desc += ")"
        player_effects.append(effect_desc)

    # --- 4. Construct the Full Prompt (Revised to avoid f-string parsing issue) ---
    prompt_parts = []
    prompt_parts.append(persona)
    prompt_parts.append("\n\nYour current stats:")
    prompt_parts.append(f"HP: {enemy_char.current_hp}/{enemy_char.max_hp}")
    prompt_parts.append(f"MP: {enemy_char.current_mp}/{enemy_char.max_mp}")
    prompt_parts.append(f"ATK: {enemy_char.current_atk}")
    prompt_parts.append(f"DEF: {enemy_char.current_def_val}")
    prompt_parts.append(f"MAG: {enemy_char.current_mag}")
    prompt_parts.append(f"RES: {enemy_char.current_res}")
    prompt_parts.append(f"Active effects on you: {', '.join(enemy_effects) if enemy_effects else 'None'}.")
    prompt_parts.append("\n\nThe player's current stats:")
    prompt_parts.append(f"HP: {player_char.current_hp}/{player_char.max_hp}")
    prompt_parts.append(f"MP: {player_char.current_mp}/{player_char.max_mp}")
    prompt_parts.append(f"ATK: {player_char.current_atk}")
    prompt_parts.append(f"DEF: {player_char.current_def_val}")
    prompt_parts.append(f"MAG: {player_char.current_mag}")
    prompt_parts.append(f"RES: {player_char.current_res}")
    prompt_parts.append(f"Active effects on player: {', '.join(player_effects) if player_effects else 'None'}.")
    prompt_parts.append("\n\nYour available moves (ensure you have enough MP to cast them, and note their detailed effects):")
    prompt_parts.append('\n'.join(available_moves_for_prompt) if available_moves_for_prompt else 'No affordable moves.')
    prompt_parts.append(f"\n\nYour last move used was: '{enemy_char.last_move_used if enemy_char.last_move_used else 'None'}'.")
    prompt_parts.append(f"Your last attack was a critical hit: {enemy_char.last_attack_critical}.")
    prompt_parts.append("\n\nInstructions:")
    prompt_parts.append("1. Select the single best move from your available moves based on the current battle situation.")
    prompt_parts.append("2. DO NOT use the same move twice in a row, UNLESS your last attack was a critical hit (in which case, choose the best move even if it's the same one, and consider this the only exception to the rule).")
    prompt_parts.append("3. You MUST respond ONLY with the exact name of the chosen move. Do not include any other text, punctuation, or formatting.")
    prompt_parts.append("4. Ensure the chosen move's MP cost does not exceed your current MP.")
    prompt_parts.append("5. If no affordable moves are available (even if the prompt says 'No affordable moves'), respond with the name of your most basic attack regardless of cost (e.g., 'Punch' or your first listed physical attack).")
    prompt_parts.append("\nChosen Move:")

    prompt = "\n".join(prompt_parts) # Join all parts with newlines

    # Debugging the prompt itself is crucial for development
    print("\n--- Gemini AI Prompt ---")
    print(prompt)
    print("------------------------")

    # Fallback if no moves are affordable (this should rarely be hit if instruction 5 is followed)
    # Get a list of all enemy's moves (Move objects), regardless of MP
    all_enemy_moves = list(enemy_char.moves.values())
    fallback_move_name = all_enemy_moves[0].name if all_enemy_moves else "Punch"


    try:
        # `temperature` around 0.7 for a balance of creativity and consistency.
        # `max_output_tokens` should be small as we expect only a move name.
        response = model.generate_content(prompt, generation_config={"temperature": 0.7, "max_output_tokens": 50})
        chosen_move_name = response.text.strip()
        print(f"DEBUG: Gemini raw choice: '{chosen_move_name}'")
        
        # --- 5. Post-AI Validation (CRITICAL for robustness) ---
        # 1. Check if the chosen move is actually in the enemy's equipped move set
        if chosen_move_name not in enemy_char.moves:
            print(f"WARNING: Gemini chose an invalid move '{chosen_move_name}'. Falling back to random.")
            raise ValueError("Invalid move chosen by AI.")
        
        # 2. Check if the chosen move's MP cost is affordable (Gemini should adhere, but confirm)
        selected_move_obj = enemy_char.moves[chosen_move_name]
        if enemy_char.current_mp < selected_move_obj.cost:
            print(f"WARNING: Gemini chose '{chosen_move_name}' but enemy has insufficient MP ({enemy_char.current_mp} < {selected_move_obj.cost}). Falling back to random.")
            raise ValueError("Insufficient MP for chosen move.")
            
        # 3. Check 'no repeat' rule (Gemini should adhere, but confirm for safety)
        if (enemy_char.last_move_used == chosen_move_name and 
            not enemy_char.last_attack_critical and
            enemy_char.last_move_used is not None):
            print(f"WARNING: Gemini chose '{chosen_move_name}' again without critical hit. Falling back to random.")
            raise ValueError("AI repeated move without critical hit.")

        # If all validations pass
        return chosen_move_name

    except Exception as e:
        print(f"ERROR: Gemini AI call failed or returned invalid response: {e}. Falling back to random move selection.")
        # --- Fallback to random move selection ---
        # Create a pool of affordable moves, excluding the last one if it wasn't a crit
        fallback_moves_pool = []
        for m_name, m_obj in enemy_char.moves.items():
            if enemy_char.current_mp >= m_obj.cost:
                # If last move was a crit, or if this is not the last move, add it
                if enemy_char.last_attack_critical or m_name != enemy_char.last_move_used:
                    fallback_moves_pool.append(m_obj)
        
        if fallback_moves_pool:
            return random.choice(fallback_moves_pool).name
        elif all_enemy_moves: # If no affordable moves (or only last move not-crit), choose randomly from all moves regardless of cost
            print("INFO: No affordable or non-repeated moves available, choosing from all available moves.")
            return random.choice(all_enemy_moves).name
        else: # Absolutely no moves defined for the enemy
            return fallback_move_name # This should be "Punch" or a sensible default
# --- create_enemy function (updated to load image) ---
def create_enemy(enemy_name):
    print(f"DEBUG: Attempting to create enemy: {enemy_name}")
    if enemy_name not in enemy_templates:
        print(f"FATAL ERROR: Enemy template '{enemy_name}' not found.")
        sys.exit()

    template = enemy_templates[enemy_name]
    try:
        enemy_image = load_image_with_cache(template.get("image_path", "images/placeholder.png"), size=(150, 150))
        
        enemy_obj = Character(
            template["name"],
            template["hp"],
            template["atk"],
            template["def"],
            template["mag"],
            template["res"],
            enemy_image,
            max_mp=template.get("mp", 0)
        )

        for move_name in template.get("moves", []):
            if move_name in all_moves:
                enemy_obj.add_move(all_moves[move_name])
            else:
                print(f"WARNING: Enemy move '{move_name}' for '{enemy_obj.name}' not found.")
        
        print(f"DEBUG: Enemy '{enemy_name}' fully initialized with moves: {list(enemy_obj.moves.keys())}")
        return enemy_obj
    except KeyError as ke:
        print(f"FATAL ERROR: Missing key in enemy template for '{enemy_name}': {ke}.")
        sys.exit()
    except Exception as e:
        print(f"FATAL ERROR: An unexpected error occurred creating enemy '{enemy_name}': {e}")
        sys.exit()

# --- Player and Enemy Instances ---
print("DEBUG: Initializing player character...")
try:
    player_image_surface = load_image_with_cache("images/hero.png", size=(150, 150))
    player = Character("Hero", 80, 20, 15, 20, 15, player_image_surface, max_mp=80)
    player_initial_moves = ["Sword", "Punch", "Spark", "Enfeeble", "Focus"]
    for move_name in player_initial_moves:
        if move_name in all_moves:
            player.add_move(all_moves[move_name])
        else:
            print(f"WARNING: Player's initial move '{move_name}' not found.")
    print(f"DEBUG: Player initialized with moves: {list(player.moves.keys())}")
except Exception as e:
    print(f"FATAL ERROR: Failed to initialize player: {e}")
    sys.exit()

print("DEBUG: Initializing initial enemy...")
try:
    enemy = create_enemy("Goblin") # Initial enemy
    print(f"DEBUG: Initial enemy '{enemy.name}' created.")
except Exception as e:
    print(f"FATAL ERROR: Failed to create initial enemy 'Goblin': {e}")
    sys.exit()

# --- Game Progression Variables ---
current_level = 1
selected_stat_for_level_up = None
selected_double_increase_stat = None
stat_choice_preview = None

# --- Global Game Functions ---
def add_battle_message(message, color=WHITE):
    global battle_message_queue
    battle_message_queue.append({"text": message, "color": color})

def clear_battle_messages():
    global battle_message_queue, current_display_message
    battle_message_queue = []
    current_display_message = {"text": "", "color": WHITE}

def advance_battle_message():
    global current_display_message, battle_message_queue, current_combat_sub_state
    if battle_message_queue:
        current_display_message = battle_message_queue.pop(0)
    else:
        if not player.is_alive():
            end_game_lose()
        elif not enemy.is_alive():
            end_game_win()
        else:
            current_combat_sub_state = PLAYER_CHOOSING_ACTION
            add_battle_message("Choose your action!")
            current_display_message = battle_message_queue.pop(0)

# --- Music Control Functions ---
def load_and_play_music(file_path, loops=-1):
    """
    Loads and plays a music file.
    - loops = -1 for infinite loop (combat music)
    - loops = 0 for play once (level up music, will stop after playing)
    """
    global current_music_playing
    if not os.path.exists(file_path):
        print(f"WARNING: Music file not found: {file_path}")
        return

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(loops)
        current_music_playing = file_path
        print(f"DEBUG: Playing music: {file_path} with {loops} loops.")
    except pygame.error as e:
        print(f"ERROR: Could not play music file {file_path}: {e}")

def stop_music():
    """Stops any currently playing music."""
    global current_music_playing
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        print(f"DEBUG: Stopped music: {current_music_playing}")
        current_music_playing = None

def play_combat_music():
    """Plays the main combat loop music."""
    stop_music()
    load_and_play_music(COMBAT_MUSIC_PATH, loops=-1)

def play_level_up_music():
    """Plays the level-up fanfare once."""
    stop_music()
    load_and_play_music(LEVEL_UP_MUSIC_PATH, loops=0)

def play_title_music():
    """Plays the title screen music (or silence if none)."""
    stop_music()
    # If you have title music: load_and_play_music(TITLE_MUSIC_PATH, loops=-1)
    # Otherwise, just silence for now.
    pass


# --- NEW: Validation function to check if a move can be used ---
def process_turn_if_valid(move):
    """Checks if the move can be used before processing the turn."""
    global current_combat_sub_state
    
    # Check MP cost for magic or status moves
    # Only check if the move has a cost greater than 0
    if move.cost > 0 and (move.type == "magic" or move.type == "status"):
        if player.current_mp < move.cost:
            add_battle_message(f"Not enough MP to use {move.name}!", RED)
            advance_battle_message() 
            return 
            
    # If all checks pass, proceed to process the turn
    process_turn(move)

# --- REVISED: process_turn function to handle move speed, turn order, and MP cost ---
def process_turn(player_move):
    global player, enemy, current_combat_sub_state, battle_message_queue, AI_MODE, IS_GEMINI_AVAILABLE

    # Increment the move counter for the player's chosen move type
    if player_move.type == "physical":
        player.weapon_moves_used += 1
    elif player_move.type == "magic" or player_move.type == "status":
        player.magic_moves_used += 1

    # Set state to processing to prevent further input
    current_combat_sub_state = PROCESSING_TURN
    clear_battle_messages() # Clear old messages

    # --- Enemy chooses move based on AI_MODE ---
    enemy_chosen_move_obj = None
    if AI_MODE == "Realistic" and IS_GEMINI_AVAILABLE:
        # Pass the raw moves data to the AI function
        chosen_move_name = choose_ai_move(enemy, player, all_moves_json_data) 
        # Retrieve the actual Move object
        enemy_chosen_move_obj = enemy.moves.get(chosen_move_name)
        if enemy_chosen_move_obj is None: # Fallback if AI chose an invalid or non-existent move
            print(f"WARNING: AI chose '{chosen_move_name}', which is not in enemy's move set. Falling back to random.")
            # Fallback logic identical to what's inside choose_ai_move's exception handler
            affordable_moves = [move_obj for move_obj in enemy.moves.values() if enemy.current_mp >= move_obj.cost]
            fallback_moves_pool = [m for m in affordable_moves if m.name != enemy.last_move_used or enemy.last_attack_critical]
            if fallback_moves_pool:
                enemy_chosen_move_obj = random.choice(fallback_moves_pool)
            elif affordable_moves:
                enemy_chosen_move_obj = random.choice(affordable_moves)
            else:
                enemy_chosen_move_obj = list(enemy.moves.values())[0] if enemy.moves else Move("Punch", 0, [1, 2], "physical", 0, "enemy", "A desperate punch.")

    else: # AI_MODE == "Random" or Gemini is not available
        # Filter moves by MP cost before random choice
        affordable_moves = [move_obj for move_obj in enemy.moves.values() if enemy.current_mp >= move_obj.cost]
        
        # Random AI also attempts to avoid repeating a move if it wasn't a critical hit
        random_ai_pool = [m for m in affordable_moves if m.name != enemy.last_move_used or enemy.last_attack_critical]
        
        if random_ai_pool:
            enemy_chosen_move_obj = random.choice(random_ai_pool)
        elif affordable_moves: # If only the last move is affordable and no crit, use it
            enemy_chosen_move_obj = random.choice(affordable_moves)
        else:
            # Fallback if no moves are affordable or available (e.g., a "Struggle" move, or just the first move)
            print(f"DEBUG: {enemy.name} has no affordable moves. Defaulting to first available move.")
            enemy_chosen_move_obj = list(enemy.moves.values())[0] if enemy.moves else Move("Punch", 0, [1, 2], "physical", 0, "enemy", "A desperate punch.")


    # --- Determine turn order based on move speed and debuffs (lower effective speed goes first) ---
    player_effective_speed = player_move.speed + player.speed_debuff
    enemy_effective_speed = enemy_chosen_move_obj.speed + enemy.speed_debuff

    # Clear old speed debuffs AFTER this turn's speed calculation
    player.speed_debuff = 0
    enemy.speed_debuff = 0

    turn_order = []
    if player_effective_speed <= enemy_effective_speed:
        turn_order = [(player, player_move, enemy), (enemy, enemy_chosen_move_obj, player)]
    else:
        turn_order = [(enemy, enemy_chosen_move_obj, player), (player, player_move, enemy)]

    # --- Execute turns in order ---
    for attacker, move, defender in turn_order:
        # Check if the battle is already over
        if not player.is_alive() or not enemy.is_alive():
            break

        # NEW: Call start_turn for the current attacker
        attacker.start_turn()

        add_battle_message(f"--- {attacker.name}'s turn ---")
        add_battle_message(f"{attacker.name} used {move.name}!")

        # --- DEDUCT MP AFTER THE MOVE IS EXECUTED ---
        # Note: Player MP cost is already handled by process_turn_if_valid.
        # Enemy MP cost needs to be handled here.
        if attacker != enemy and move.cost > 0:
            attacker.use_mp(move.cost)

        # --- Handle different move types ---
        is_critical_hit = False # Initialize to False for each attack
        if move.type == "physical" or move.type == "magic":
            # calculate_damage should return (damage_amount, is_critical_hit)
            damage_result = move.calculate_damage(attacker, defender)
            
            if damage_result == "miss":
                add_battle_message(f"{attacker.name}'s {move.name} missed!")
            else:
                damage, is_critical_hit = damage_result # Unpack the tuple
                if is_critical_hit:
                    add_battle_message("CRITICAL HIT!", GOLD)
                defender.take_damage(damage)
                add_battle_message(f"{defender.name} took {damage} damage!")
                
                # Apply status effect if any (for damaging moves)
                if move.status_effect_data:
                    defender.apply_status_effect(move.status_effect_data)
                    add_battle_message(f"{defender.name} is afflicted with {move.status_effect_data['name']}!", BLUE)

        elif move.type == "heal":
            # Determine target for heal move: if move.target is "self", target is attacker; otherwise, target is defender
            target_character = attacker if move.target == "self" else defender
            if move.heal_range:
                heal_amount = random.randint(move.heal_range[0], move.heal_range[1])
                target_character.heal(heal_amount)
                add_battle_message(f"{target_character.name} regenerated {heal_amount} health!")
            else:
                add_battle_message(f"{attacker.name}'s {move.name} had no healing effect.", RED)

        elif move.type == "status": # For non-damaging status moves
            # Determine target for status move: if move.target is "self", target is attacker; otherwise, target is defender
            target_character = attacker if move.target == "self" else defender
            if move.status_effect_data:
                target_character.apply_status_effect(move.status_effect_data)
                add_battle_message(f"{target_character.name} is afflicted with {move.status_effect_data['name']}!", BLUE)
            else:
                add_battle_message(f"{attacker.name} used {move.name} with no direct effect.", GRAY)

        # --- UPDATE ATTACKER'S LAST MOVE AND CRIT STATUS ---
        attacker.last_move_used = move.name
        attacker.last_attack_critical = is_critical_hit
        # --- END UPDATE ---

        # NEW: Call end_turn for the current attacker
        attacker.end_turn()
        
    # After both turns are processed, set the state to wait for player input
    current_combat_sub_state = WAITING_FOR_PLAYER_INPUT_TO_PROGRESS
    advance_battle_message() # Display the first message in the queue

def start_combat():
    global current_game_state, player, enemy, displaying_stats, current_combat_sub_state, current_level
    current_game_state = COMBAT_SCREEN
    current_combat_sub_state = PLAYER_CHOOSING_ACTION
    displaying_stats = False
    clear_battle_messages()
    player.reset_move_counters() # Reset move counters at the start of a new combat encounter

    # --- Play Combat Music ---
    play_combat_music()

    # --- UPDATED: Tiered enemy spawning logic based on player level ---
    beginner_enemies = ["Goblin", "Slime", "Giant Rat", "Kobold"]
    easy_enemies = ["Dire Wolf", "Skeleton", "Zombie", "Giant Spider", "Goblin Shaman"]
    medium_enemies = ["Gnoll", "Troll", "Golem", "Gargoyle", "Banshee", "Bandit"]
    hard_enemies = ["Ogre", "Minotaur", "Dark Mage", "Gorgon", "Basilisk"]
    deadly_enemies = ["Gryphon", "Automaton", "Vampire", "Manticore", "Dread Knight"]
    final_bosses = ["Hydra", "Dragon", "Sharktocrab", "Beholder", "Giant"]

    enemy_pool = []
    if current_level >= 26:
        enemy_pool = final_bosses
    elif current_level >= 21:
        enemy_pool = deadly_enemies
    elif current_level >= 16:
        enemy_pool = hard_enemies
    elif current_level >= 11:
        enemy_pool = medium_enemies
    elif current_level >= 6:
        enemy_pool = easy_enemies
    else: # Levels 1-5
        enemy_pool = beginner_enemies

    # Check if any enemy from the selected pool exists in the loaded templates
    valid_enemies = [e for e in enemy_pool if e in enemy_templates]
    
    if not valid_enemies:
        print(f"WARNING: No enemy templates found for level tier {current_level}. Defaulting to beginner enemies.")
        valid_enemies = [e for e in beginner_enemies if e in enemy_templates]
        if not valid_enemies:
            print("FATAL ERROR: No valid enemy templates found at all. Check enemies.json.")
            sys.exit()
    
    enemy_to_create = random.choice(valid_enemies)
    enemy = create_enemy(enemy_to_create)
    
    add_battle_message(f"A wild {enemy.name} appeared!")
    add_battle_message("Choose your action!")
    advance_battle_message()

def end_game_lose():
    global current_game_state
    current_game_state = GAME_OVER_SCREEN
    clear_battle_messages()
    stop_music() # Stop combat music on game over

def end_game_win():
    global current_game_state, selected_stat_for_level_up, selected_double_increase_stat, stat_choice_preview
    current_game_state = LEVEL_UP_SCREEN
    player.heal(player.max_hp)
    player.restore_mp(player.max_mp)
    selected_stat_for_level_up = None
    selected_double_increase_stat = None
    stat_choice_preview = None
    clear_battle_messages()
    add_battle_message("You won the battle!")
    
    # --- Play Level Up Music ---
    play_level_up_music()

def go_to_title():
    global current_game_state, current_level, player, enemy, AI_MODE, IS_GEMINI_AVAILABLE
    current_game_state = TITLE_SCREEN
    current_level = 1
    # Re-initialize player to default stats and image
    player_image_surface = load_image_with_cache("images/hero.png", size=(150, 150))
    player = Character("Hero", 80, 20, 15, 20, 15, player_image_surface, max_mp=80)
    # Reset AI mode and re-check connectivity for next game
    AI_MODE = "Random" # Reset to default
    check_internet_connectivity() # Re-check on return to title
    for move_name in ["Sword", "Punch", "Spark", "Enfeeble", "Focus"]:
        if move_name in all_moves:
            player.add_move(all_moves[move_name])
    enemy = create_enemy("Goblin")
    clear_battle_messages()
    
    # --- Stop any music or play title music ---
    play_title_music()

def toggle_stats_display():
    global displaying_stats
    # Only allow toggling if not in the middle of a turn
    if current_combat_sub_state not in [PROCESSING_TURN, WAITING_FOR_PLAYER_INPUT_TO_PROGRESS]:
        displaying_stats = not displaying_stats
        if not displaying_stats: # If stats are now OFF, display the action prompt
            if current_combat_sub_state == PLAYER_CHOOSING_ACTION: # Only if already in main action menu
                # Only re-add message if queue is empty or if we're not currently processing/waiting
                if not battle_message_queue and current_combat_sub_state == PLAYER_CHOOSING_ACTION:
                    add_battle_message("Choose your action!")
                    current_display_message = battle_message_queue.pop(0)

def go_to_weapon_menu():
    global current_combat_sub_state
    current_combat_sub_state = PLAYER_CHOOSING_WEAPON_MOVE
    add_battle_message("Choose a Weapon move:")
    advance_battle_message()

def go_to_magic_menu():
    global current_combat_sub_state
    current_combat_sub_state = PLAYER_CHOOSING_MAGIC_MOVE
    add_battle_message("Choose a Magic move:")
    advance_battle_message()

def go_back_to_main_action_menu():
    global current_combat_sub_state
    current_combat_sub_state = PLAYER_CHOOSING_ACTION
    add_battle_message("Choose your action!")
    advance_battle_message()

# --- Level Up Functions ---
def choose_stat(stat_name):
    global selected_stat_for_level_up, selected_double_increase_stat, stat_choice_preview
    
    # If the user clicks on a stat that is already selected, deselect it
    if selected_stat_for_level_up == stat_name:
        selected_stat_for_level_up = None
        # If the first selected stat is deselected, also deselect the second if it exists
        if selected_double_increase_stat and stat_name == selected_double_increase_stat:
            selected_double_increase_stat = None
    elif selected_double_increase_stat == stat_name:
        selected_double_increase_stat = None
        
    # If the user has not chosen the first stat yet, choose it
    elif selected_stat_for_level_up is None:
        selected_stat_for_level_up = stat_name
    # If the user has chosen the first stat and is now choosing the double increase
    elif selected_double_increase_stat is None and stat_name not in ['HP', 'MP'] and stat_name != selected_stat_for_level_up:
        selected_double_increase_stat = stat_name
    # If the user clicks on a forbidden stat for the double increase, do nothing
    elif selected_stat_for_level_up and stat_name in ['HP', 'MP'] and stat_name != selected_stat_for_level_up:
        pass # Do nothing, they can't choose HP or MP for the double increase unless it's the first selection
        
    
    # --- Update the preview text based on choices ---
    stat_choice_preview = []
    if selected_stat_for_level_up:
        current_val_1 = 0
        increase_1 = 0
        if selected_stat_for_level_up == 'ATK': current_val_1, increase_1 = player.atk, 1
        elif selected_stat_for_level_up == 'DEF': current_val_1, increase_1 = player.def_val, 1
        elif selected_stat_for_level_up == 'MAG': current_val_1, increase_1 = player.mag, 1
        elif selected_stat_for_level_up == 'RES': current_val_1, increase_1 = player.res, 1
        elif selected_stat_for_level_up == 'HP': current_val_1, increase_1 = player.max_hp, 5
        elif selected_stat_for_level_up == 'MP': current_val_1, increase_1 = player.max_mp, 5
        
        stat_choice_preview.append((selected_stat_for_level_up, current_val_1, current_val_1 + increase_1))
        
    if selected_double_increase_stat:
        current_val_2 = 0
        increase_2 = 2 # Default values; actual values depend on player.level in confirm_level_up_choice
        if selected_double_increase_stat == 'ATK': current_val_2 = player.atk
        elif selected_double_increase_stat == 'DEF': current_val_2 = player.def_val
        elif selected_double_increase_stat == 'MAG': current_val_2 = player.mag
        elif selected_double_increase_stat == 'RES': current_val_2 = player.res
        stat_choice_preview.append((selected_double_increase_stat, current_val_2, current_val_2 + increase_2))

    if not stat_choice_preview:
        stat_choice_preview = None


def confirm_level_up_choice():
    global current_game_state, current_level, selected_stat_for_level_up, selected_double_increase_stat, stat_choice_preview, enemy
    
    # --- Determine stat increase amounts based on player level ---
    single_increase_amount = 1
    double_increase_amount = 2
    hp_mp_increase_amount = 5
    conditional_boost_amount = 2       # Boost for primary conditional stat (HP or MP)
    conditional_balanced_hp_boost = 1  # Boost for balanced style (always HP)

    if player.level >= 21: # Deadly Tier (Level 21 and above)
        single_increase_amount = 3
        double_increase_amount = 4
        hp_mp_increase_amount = 9
        conditional_boost_amount = 6
        conditional_balanced_hp_boost = 3 # Half of the conditional_boost_amount for deadly tier
    elif player.level >= 11: # Medium Tier (Level 11 to 20)
        single_increase_amount = 2
        double_increase_amount = 3
        hp_mp_increase_amount = 7
        conditional_boost_amount = 4
        conditional_balanced_hp_boost = 2 # Half of the conditional_boost_amount for medium tier

    # Only confirm if a stat for a single increase and a double increase are selected
    if selected_stat_for_level_up and selected_double_increase_stat:
        
        # Apply the single increase
        if selected_stat_for_level_up == 'ATK': player.atk += single_increase_amount
        elif selected_stat_for_level_up == 'DEF': player.def_val += single_increase_amount
        elif selected_stat_for_level_up == 'MAG': player.mag += single_increase_amount
        elif selected_stat_for_level_up == 'RES': player.res += single_increase_amount
        elif selected_stat_for_level_up == 'HP': 
            player.max_hp += hp_mp_increase_amount
            player.current_hp += hp_mp_increase_amount
        elif selected_stat_for_level_up == 'MP':
            player.max_mp += hp_mp_increase_amount
            player.current_mp += hp_mp_increase_amount

        # Apply the double increase
        if selected_double_increase_stat == 'ATK': player.atk += double_increase_amount
        elif selected_double_increase_stat == 'DEF': player.def_val += double_increase_amount
        elif selected_double_increase_stat == 'MAG': player.mag += double_increase_amount
        elif selected_double_increase_stat == 'RES': player.res += double_increase_amount
        
        # Apply the bonus increase based on combat actions
        if player.weapon_moves_used >= player.magic_moves_used: # Note: Used >= here as discussed previously
            player.max_hp += conditional_boost_amount
            player.current_hp += conditional_boost_amount
            add_battle_message(f"Your physical training has paid off! HP increased by {conditional_boost_amount}.", GREEN)
        elif player.magic_moves_used > player.weapon_moves_used:
            player.max_mp += conditional_boost_amount
            player.current_mp += conditional_boost_amount
            add_battle_message(f"Your magical aptitude grows! MP increased by {conditional_boost_amount}.", BLUE)
        else: # Balanced fighting style
            add_battle_message("You maintained a balanced fighting style.", WHITE)
            player.max_hp += conditional_balanced_hp_boost
            player.current_hp += conditional_balanced_hp_boost
            
        player.level += 1 # Assuming player.level is the source of the player's level
        global current_level # Also update global game level if used for enemy scaling
        current_level += 1

        selected_stat_for_level_up = None
        selected_double_increase_stat = None
        stat_choice_preview = None # Clear the preview for the next level-up
        
        # The game flow after level-up confirmation (starts combat)
        start_combat()

# --- Player Move Execution Functions (Updated to use validation) ---
def execute_player_sword(): process_turn_if_valid(all_moves["Sword"])
def execute_player_punch(): process_turn_if_valid(all_moves["Punch"])
def execute_player_spark(): process_turn_if_valid(all_moves["Spark"])
def execute_player_enfeeble(): process_turn_if_valid(all_moves["Enfeeble"])
def execute_player_focus(): process_turn_if_valid(all_moves["Focus"])

# --- NEW: Function to draw wrapped text ---
def draw_wrapped_text(surface, text, color, rect, font, antialias=True):
    """Draws text that wraps to the next line when it exceeds the width of the rectangle."""
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        # Check if adding the next word (plus a space) exceeds the rect width
        if font.size(current_line + word + " ")[0] <= rect.width:
            current_line += word + " "
        else:
            lines.append(current_line.strip()) # Add the current line, remove trailing space
            current_line = word + " " # Start new line with current word
    lines.append(current_line.strip()) # Add the last line

    y = rect.top
    for line in lines:
        line_surface = font.render(line, antialias, color)
        # Center the text horizontally within the rect
        text_rect = line_surface.get_rect(centerx=rect.centerx, y=y)
        surface.blit(line_surface, text_rect)
        y += font.get_linesize()

# --- Buttons ---
initiate_combat_button = Button(
    SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 70,
    "Initiate Combat", font_medium, LIGHT_BLUE, WHITE, start_combat
)

# NEW: AI Mode Buttons for Title Screen
random_ai_button = Button(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 120, 100, 40, "Random AI", font_small, (50, 150, 50), WHITE)
realistic_ai_button = Button(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 120, 100, 40, "Realistic AI", font_small, (50, 150, 50), RED)
# END NEW AI Mode Buttons

# Main action buttons: "Stats" is always available to toggle
main_action_buttons = [
    Button(50, SCREEN_HEIGHT - 100, 150, 60, "Weapon", font_small, GRAY, WHITE, go_to_weapon_menu,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_ACTION),
    Button(220, SCREEN_HEIGHT - 100, 150, 60, "Magic", font_small, GRAY, WHITE, go_to_magic_menu,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_ACTION),
    Button(390, SCREEN_HEIGHT - 100, 150, 60, "Stats", font_small, GRAY, WHITE, toggle_stats_display,
           enabled_func=lambda: current_combat_sub_state not in [PROCESSING_TURN, WAITING_FOR_PLAYER_INPUT_TO_PROGRESS]),
    Button(560, SCREEN_HEIGHT - 100, 150, 60, "Forfeit", font_small, GRAY, WHITE, end_game_lose,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_ACTION),
]

weapon_move_buttons = [
    Button(50, SCREEN_HEIGHT - 100, 150, 60, "Sword", font_small, GRAY, WHITE, execute_player_sword,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_WEAPON_MOVE),
    Button(220, SCREEN_HEIGHT - 100, 150, 60, "Punch", font_small, GRAY, WHITE, execute_player_punch,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_WEAPON_MOVE),
    Button(390, SCREEN_HEIGHT - 100, 150, 60, "Back", font_small, GRAY, WHITE, go_back_to_main_action_menu,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_WEAPON_MOVE)
]

magic_move_buttons = [
    Button(50, SCREEN_HEIGHT - 100, 150, 60, "Spark", font_small, GRAY, WHITE, execute_player_spark,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_MAGIC_MOVE),
    Button(220, SCREEN_HEIGHT - 100, 150, 60, "Enfeeble", font_small, GRAY, WHITE, execute_player_enfeeble,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_MAGIC_MOVE and "Enfeeble" in player.moves),
    Button(390, SCREEN_HEIGHT - 100, 150, 60, "Focus", font_small, GRAY, WHITE, execute_player_focus,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_MAGIC_MOVE and "Focus" in player.moves),
    Button(560, SCREEN_HEIGHT - 100, 150, 60, "Back", font_small, GRAY, WHITE, go_back_to_main_action_menu,
           enabled_func=lambda: not displaying_stats and current_combat_sub_state == PLAYER_CHOOSING_MAGIC_MOVE)
]

level_up_buttons = [
    Button(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 200, 100, 50, "ATK", font_small, LIGHT_BLUE, WHITE, lambda: choose_stat('ATK'),
           enabled_func=lambda: selected_double_increase_stat != 'ATK' and selected_stat_for_level_up != 'ATK'),
    Button(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 200, 100, 50, "DEF", font_small, LIGHT_BLUE, WHITE, lambda: choose_stat('DEF'),
           enabled_func=lambda: selected_double_increase_stat != 'DEF' and selected_stat_for_level_up != 'DEF'),
    Button(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 200, 100, 50, "MAG", font_small, LIGHT_BLUE, WHITE, lambda: choose_stat('MAG'),
           enabled_func=lambda: selected_double_increase_stat != 'MAG' and selected_stat_for_level_up != 'MAG'),
    Button(SCREEN_WIDTH // 2 + 140, SCREEN_HEIGHT - 200, 100, 50, "RES", font_small, LIGHT_BLUE, WHITE, lambda: choose_stat('RES'),
           enabled_func=lambda: selected_double_increase_stat != 'RES' and selected_stat_for_level_up != 'RES'),
    Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT - 130, 100, 50, "HP", font_small, LIGHT_BLUE, WHITE, lambda: choose_stat('HP'),
           enabled_func=lambda: selected_stat_for_level_up != 'HP'),
    Button(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 130, 100, 50, "MP", font_small, LIGHT_BLUE, WHITE, lambda: choose_stat('MP'),
           enabled_func=lambda: selected_stat_for_level_up != 'MP')
]

confirm_button = Button(
    SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 60, 150, 60, "Confirm", font_medium, GREEN, WHITE, confirm_level_up_choice,
    enabled_func=lambda: selected_stat_for_level_up is not None and selected_double_increase_stat is not None
)

back_to_title_button = Button(
    SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 70,
    "Back to Title", font_medium, LIGHT_BLUE, WHITE, go_to_title
)

win_to_title_button = Button(
    SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 70,
    "Back to Title", font_medium, LIGHT_BLUE, WHITE, go_to_title
)

# --- Game Loop ---
print("DEBUG: Entering game loop...")
running = True
clock = pygame.time.Clock()
FPS = 60

# --- Initial Connectivity Check at Game Startup ---
check_internet_connectivity()

# Start with title screen music (or silence)
play_title_music()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if current_game_state == COMBAT_SCREEN and current_combat_sub_state == WAITING_FOR_PLAYER_INPUT_TO_PROGRESS and event.key == pygame.K_SPACE:
                advance_battle_message()
            if current_game_state == COMBAT_SCREEN and event.key == pygame.K_ESCAPE and displaying_stats:
                toggle_stats_display()
            elif current_game_state == COMBAT_SCREEN and event.key == pygame.K_ESCAPE and \
                 (current_combat_sub_state == PLAYER_CHOOSING_WEAPON_MOVE or current_combat_sub_state == PLAYER_CHOOSING_MAGIC_MOVE) and \
                 current_combat_sub_state not in [PROCESSING_TURN, WAITING_FOR_PLAYER_INPUT_TO_PROGRESS]:
                go_back_to_main_action_menu()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_game_state == COMBAT_SCREEN and current_combat_sub_state == WAITING_FOR_PLAYER_INPUT_TO_PROGRESS:
                advance_battle_message()
            if current_game_state == TITLE_SCREEN:
                initiate_combat_button.handle_event(event)
                # NEW: Handle AI Mode button clicks
                if random_ai_button.handle_event(event):
                    AI_MODE = "Random"
                    add_battle_message("AI Mode set to Random. (Enemy will choose moves randomly)", ORANGE)
                    # No connectivity check needed for Random mode, just clear previous messages
                    clear_battle_messages()
                    current_display_message = {"text": "AI Mode: Random", "color": ORANGE} # Display immediately
                elif realistic_ai_button.handle_event(event):
                    AI_MODE = "Realistic"
                    add_battle_message("Checking internet connectivity for Realistic AI...", ORANGE)
                    clear_battle_messages() # Clear old messages
                    current_display_message = {"text": "Checking connectivity...", "color": ORANGE} # Display immediately
                    pygame.display.flip() # Update screen to show message
                    
                    # Re-check connectivity ONLY if Realistic is selected
                    if check_internet_connectivity():
                        add_battle_message("Realistic AI enabled! (Enemy will choose moves intelligently)", GREEN)
                    else:
                        AI_MODE = "Random" # Fallback if check fails
                        add_battle_message("Realistic AI unavailable. Defaulting to Random AI.", RED)
                    # After check, display the first new message
                    if battle_message_queue: # Ensure there's a message to show
                        current_display_message = battle_message_queue.pop(0)

            elif current_game_state == COMBAT_SCREEN:
                # Determine which set of buttons is currently active for event handling
                buttons_to_handle = []
                if current_combat_sub_state == PLAYER_CHOOSING_ACTION:
                    buttons_to_handle = main_action_buttons
                elif current_combat_sub_state == PLAYER_CHOOSING_WEAPON_MOVE:
                    buttons_to_handle = weapon_move_buttons
                elif current_combat_sub_state == PLAYER_CHOOSING_MAGIC_MOVE:
                    buttons_to_handle = magic_move_buttons

                for button in buttons_to_handle:
                    # A button should only handle the event if it's logically enabled
                    # AND if it's the 'Stats' button, or if stats aren't being displayed (for other buttons)
                    if button.enabled_func(): # Check the button's own enabled_func first
                        if button.text == "Stats": # Stats button is always clickable to toggle display
                            button.handle_event(event)
                        elif not displaying_stats: # Other buttons only respond if stats overlay is not active
                            button.handle_event(event)

            elif current_game_state == LEVEL_UP_SCREEN:
                for button in level_up_buttons: button.handle_event(event)
                confirm_button.handle_event(event)
            elif current_game_state == GAME_OVER_SCREEN:
                back_to_title_button.handle_event(event)
            elif current_game_state == GAME_WIN_SCREEN:
                win_to_title_button.handle_event(event)

    # --- Drawing ---
    screen.fill(BLACK)

    if current_game_state == TITLE_SCREEN:
        text_surface = font_large.render(GAME_TITLE, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)) # Adjusted Y
        screen.blit(text_surface, text_rect)
        initiate_combat_button.draw(screen)

        # NEW: Draw AI Mode buttons
        random_ai_button.draw(screen)
        realistic_ai_button.draw(screen)

        # Display current AI mode status
        ai_mode_text_display = ""
        color_mode_display = WHITE
        if AI_MODE == "Realistic":
            ai_mode_text_display = "AI Mode: Realistic (Gemini)"
            color_mode_display = GREEN
            if not IS_GEMINI_AVAILABLE: # If realistic chosen but API unavailable
                ai_mode_text_display = "Realistic AI Unavailable (No Internet/API Key)"
                color_mode_display = RED
        else: # AI_MODE == "Random"
            ai_mode_text_display = "AI Mode: Random"
            color_mode_display = WHITE
        
        # Display connectivity/AI mode message at the bottom center
        current_ai_mode_message_surface = font_small.render(ai_mode_text_display, True, color_mode_display)
        current_ai_mode_message_rect = current_ai_mode_message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180))
        screen.blit(current_ai_mode_message_surface, current_ai_mode_message_rect)

        # Display battle log message queue (for connectivity check feedback)
        if current_display_message["text"]:
            message_surface = font_small.render(current_display_message["text"], True, current_display_message["color"])
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)) # Position near bottom
            screen.blit(message_surface, message_rect)


    elif current_game_state == COMBAT_SCREEN:
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 150))
        pygame.draw.rect(screen, (70, 70, 70), (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150))

        # --- Draw Character Images ---
        player_image_rect = player.image.get_rect(midbottom=(180, 300))
        screen.blit(player.image, player_image_rect)
        
        enemy_image_rect = enemy.image.get_rect(midbottom=(SCREEN_WIDTH - 180, 300))
        screen.blit(enemy.image, enemy_image_rect)

        # Display Character Names
        player_name_text = font_medium.render(player.name, True, WHITE)
        screen.blit(player_name_text, (20, 20))
        enemy_name_text = font_medium.render(enemy.name, True, WHITE)
        enemy_name_text_rect = enemy_name_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        screen.blit(enemy_name_text, enemy_name_text_rect)

        # Display Character HP & MP
        player_hp_text = font_small.render(f"HP: {player.current_hp}/{player.max_hp}", True, RED)
        screen.blit(player_hp_text, (20, 60))
        player_mp_text = font_small.render(f"MP: {player.current_mp}/{player.max_mp}", True, GREEN)
        screen.blit(player_mp_text, (20, 90))
        
        enemy_hp_text = font_small.render(f"HP: {enemy.current_hp}/{enemy.max_hp}", True, RED)
        enemy_hp_text_rect = enemy_hp_text.get_rect(topright=(SCREEN_WIDTH - 20, 60))
        screen.blit(enemy_hp_text, enemy_hp_text_rect)

        # --- Battle Log Display ---
        log_box_x, log_box_y, log_box_width, log_box_height = 50, SCREEN_HEIGHT - 250, SCREEN_WIDTH - 100, 80
        log_box_rect = pygame.Rect(log_box_x, log_box_y, log_box_width, log_box_height)
        pygame.draw.rect(screen, DARK_GRAY, log_box_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, log_box_rect, 2, border_radius=5)
        message_surface = font_small.render(current_display_message["text"], True, current_display_message["color"])
        message_rect = message_surface.get_rect(center=log_box_rect.center)
        screen.blit(message_surface, message_rect)

        # --- Draw "Press Space to Advance" hint ---
        if current_combat_sub_state == WAITING_FOR_PLAYER_INPUT_TO_PROGRESS:
            hint_text = "Press Space or Click to Advance"
            hint_surface = font_tiny.render(hint_text, True, GRAY)
            hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75))
            screen.blit(hint_surface, hint_rect)

        # --- Draw player options based on sub-state ---
        if current_combat_sub_state in [PLAYER_CHOOSING_ACTION, PLAYER_CHOOSING_WEAPON_MOVE, PLAYER_CHOOSING_MAGIC_MOVE]:
            buttons_to_draw = []
            if current_combat_sub_state == PLAYER_CHOOSING_ACTION: buttons_to_draw = main_action_buttons
            elif current_combat_sub_state == PLAYER_CHOOSING_WEAPON_MOVE: buttons_to_draw = weapon_move_buttons
            elif current_combat_sub_state == PLAYER_CHOOSING_MAGIC_MOVE: buttons_to_draw = magic_move_buttons
            
            for button in buttons_to_draw:
                # Determine visual state (dimmed if disabled by its own enabled_func or if stats are open AND it's not the 'Stats' button)
                is_visually_disabled = False
                if button.enabled_func and not button.enabled_func():
                    is_visually_disabled = True # Disabled by its own logic
                
                # Special visual dimming for other buttons when stats are open
                if displaying_stats and button.text != "Stats":
                    is_visually_disabled = True
                    
                original_color, original_text_color = button.color, button.text_color
                if is_visually_disabled:
                    button.color = (original_color[0] // 2, original_color[1] // 2, original_color[2] // 2) # Dimming
                    button.text_color = (original_text_color[0] // 2, original_text_color[1] // 2, original_text_color[2] // 2)
                
                # This is where the button is actually drawn on the screen
                button.draw(screen) 
                
                # Reset colors for the next frame, crucial if you modify them for drawing
                button.color, button.text_color = original_color, original_text_color 

        # --- Draw Stats Pop-up if active ---
        if displaying_stats:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            stats_box_width, stats_box_height = 400, 400 # Increased height from 280 to 400
            stats_box_x, stats_box_y = (SCREEN_WIDTH - stats_box_width) // 2, (SCREEN_HEIGHT - stats_box_height) // 2
            stats_box_rect = pygame.Rect(stats_box_x, stats_box_y, stats_box_width, stats_box_height)
            pygame.draw.rect(screen, DARK_GRAY, stats_box_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, stats_box_rect, 3, border_radius=10)
            stats_title = font_medium.render(f"{player.name} Stats", True, WHITE)
            screen.blit(stats_title, (stats_box_x + 20, stats_box_y + 20))
            stats_lines = player.get_stats_lines()
            line_height_offset = 70 # Keep this, it's the starting Y for the first line
            for line_text in stats_lines:
                line_surface = font_small.render(line_text, True, WHITE)
                screen.blit(line_surface, (stats_box_x + 20, stats_box_y + line_height_offset))
                line_height_offset += font_small.get_linesize() + 5 # Increment for each line
            
            # Adjust the position of the close instruction to be near the bottom of the new taller box
            close_instruction = font_tiny.render("Press 'Stats' again or ESC to close", True, GRAY)
            screen.blit(close_instruction, (stats_box_x + 20, stats_box_y + stats_box_height - 35)) # Adjusted Y position

    elif current_game_state == LEVEL_UP_SCREEN:
        level_up_title = font_large.render(f"LEVEL UP! (Level {current_level + 1})", True, GOLD)
        level_up_title_rect = level_up_title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(level_up_title, level_up_title_rect)
        
        instruction_text = font_medium.render("Choose two stats to increase:", True, WHITE)
        instruction_text_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(instruction_text, instruction_text_rect)
        
        player_stats_title = font_small.render("Your Current Stats:", True, WHITE)
        screen.blit(player_stats_title, (SCREEN_WIDTH // 2 - 200, 150))
        current_stats_y_offset = 180
        stats_data = [("HP", player.max_hp), ("MP", player.max_mp), ("ATK", player.atk), ("DEF", player.def_val), ("MAG", player.mag), ("RES", player.res)]
        for stat_name, stat_val in stats_data:
            stat_text = font_small.render(f"{stat_name}: {stat_val}", True, WHITE)
            screen.blit(stat_text, (SCREEN_WIDTH // 2 - 200, current_stats_y_offset))
            current_stats_y_offset += font_small.get_linesize() + 5
        
        # --- Draw the stat preview ---
        if stat_choice_preview:
            preview_y_offset = 200
            for stat_name, current_val, new_val in stat_choice_preview:
                preview_text = font_medium.render(f"{stat_name}: {current_val} -> {new_val}", True, WHITE)
                preview_rect = preview_text.get_rect(midleft=(SCREEN_WIDTH // 2 + 50, preview_y_offset))
                screen.blit(preview_text, preview_rect)
                preview_y_offset += font_medium.get_linesize() + 10

        # --- Draw the instruction box and text ---
        instruction_box_width = 350
        instruction_box_height = 60
        instruction_box_x = SCREEN_WIDTH // 2 + 50
        instruction_box_y = SCREEN_HEIGHT // 2 + 30
        
        instruction_box_rect = pygame.Rect(instruction_box_x, instruction_box_y, instruction_box_width, instruction_box_height)
        pygame.draw.rect(screen, DARK_GRAY, instruction_box_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, instruction_box_rect, 2, border_radius=5)

        # Define the inner rectangle for wrapped text (with padding)
        text_padding = 10
        text_rect_padding = instruction_box_rect.inflate(-2 * text_padding, -2 * text_padding)

        # Determine the instruction text
        if selected_stat_for_level_up and selected_double_increase_stat:
            confirm_instruction_text = "You have chosen your increases. Click Confirm."
        elif selected_stat_for_level_up:
            confirm_instruction_text = "Now choose a second stat for the GREATER boost (not HP or MP)."
        else:
            confirm_instruction_text = "Choose one stat for a small boost."
            
        draw_wrapped_text(screen, confirm_instruction_text, GRAY, text_rect_padding, font_tiny)

        for button in level_up_buttons:
            is_single_selected = button.text == selected_stat_for_level_up
            is_double_selected = button.text == selected_double_increase_stat
            
            # This logic determines if the button is disabled for selection purposes
            is_disabled_for_selection = (is_single_selected and is_double_selected) or \
                                        (selected_double_increase_stat is not None and button.text in ['HP', 'MP'])
            
            original_color = button.color
            if is_single_selected:
                button.color = GREEN
            elif is_double_selected:
                button.color = GOLD
            elif is_disabled_for_selection:
                button.color = (original_color[0] // 2, original_color[1] // 2, original_color[2] // 2)
            
            button.draw(screen)
            button.color = original_color

        confirm_button.draw(screen)


    elif current_game_state == GAME_OVER_SCREEN:
        game_over_surface = font_large.render("You Lose", True, WHITE)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_surface, game_over_rect)
        back_to_title_button.draw(screen)

    elif current_game_state == GAME_WIN_SCREEN:
        win_surface = font_large.render("YOU WIN!", True, GREEN)
        win_rect = win_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(win_surface, win_rect)
        win_to_title_button.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()