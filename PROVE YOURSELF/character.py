import random
import copy

class Character:
    def __init__(self, name, hp, atk, def_val, mag, res, image_surface, max_mp=0):
        self.name = name
        self.max_hp = hp
        self.current_hp = hp
        self.max_mp = max_mp
        self.current_mp = max_mp
        self.atk = atk # Base Attack
        self.def_val = def_val # Base Defense
        self.mag = mag # Base Magic
        self.res = res # Base Resistance
        self.image = image_surface # Pygame Surface object for the character image
        self.moves = {} # Dictionary to store Move objects by name
        self.level = 1

        self.last_move_used = None       # Stores the name of the last move this character used
        self.last_attack_critical = False # True if this character's last attack was a critical hit

        # New: System for complex status effects
        self.active_status_effects = [] # List of dictionaries, e.g., {'name': 'Enfeebled', 'duration': 1, 'effects': {'atk_mult': 0.5, 'mag_mult': 0.5}}
        
        # New: Counters for move types used in combat for level-up bonuses
        self.weapon_moves_used = 0
        self.magic_moves_used = 0

        # Old single debuff system (kept for backward compatibility if old moves use it, though being phased out)
        self.speed_debuff = 0 # Temporary speed modifier

    def add_move(self, move_obj):
        self.moves[move_obj.name] = move_obj

    def is_alive(self):
        return self.current_hp > 0

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

    def heal(self, amount):
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

    def use_mp(self, amount):
        self.current_mp -= amount
        if self.current_mp < 0:
            self.current_mp = 0

    def restore_mp(self, amount):
        self.current_mp += amount
        if self.current_mp > self.max_mp:
            self.current_mp = self.max_mp

    # New: Reset move counters for level-up bonus
    def reset_move_counters(self):
        self.weapon_moves_used = 0
        self.magic_moves_used = 0

    # NEW: Apply a complex status effect
    def apply_status_effect(self, effect_data):
        # Create a deep copy of the effect_data to prevent shared dictionary issues.
        # This ensures each instance of a status effect has its own mutable data (like 'duration').
        new_effect_instance = copy.deepcopy(effect_data) # <-- MODIFIED LINE

        # Check if effect with the same name already exists and refresh its duration
        for existing_effect in self.active_status_effects:
            if existing_effect['name'] == new_effect_instance['name']: # Use new_effect_instance's name
                existing_effect['duration'] = new_effect_instance['duration'] # Refresh duration with new instance's duration
                print(f"DEBUG: Refreshed {new_effect_instance['name']} on {self.name}. New duration: {existing_effect['duration']}")
                return
        
        # If effect doesn't exist, add the new instance
        self.active_status_effects.append(new_effect_instance) # <-- Use new_effect_instance
        print(f"DEBUG: Applied {new_effect_instance['name']} to {self.name}. Initial duration: {new_effect_instance['duration']}. Active effects: {self.active_status_effects}")

    # NEW: Helper to get effective stat values considering status effects
    # NEW: Helper to get effective stat values considering status effects
    def _get_effective_stat(self, base_stat, stat_name):
        modifier = 1.0 # Multiplier for percentage effects
        flat_modifier = 0 # Flat addition/subtraction

        for effect in self.active_status_effects:
            # Handle stat_modifier (flat changes like from "Endure")
            # This covers effects where stat changes are directly in 'stat_modifier' dict
            if 'stat_modifier' in effect and stat_name in effect['stat_modifier']:
                flat_modifier += effect['stat_modifier'][stat_name]

            # Handle generic 'effects' dictionary (if used for other types like percentage or flat)
            if 'effects' in effect:
                # Apply percentage modifiers
                if f'{stat_name}_mult' in effect['effects']:
                    modifier *= effect['effects'][f'{stat_name}_mult']
                # Apply flat modifiers (this catches _flat from 'effects' dictionary)
                if f'{stat_name}_flat' in effect['effects']:
                    flat_modifier += effect['effects'][f'{stat_name}_flat']
        
        return max(0, int(base_stat * modifier) + flat_modifier) # Ensure stat doesn't go below zero

    # NEW: Properties to get current effective stats
    @property
    def current_atk(self):
        return self._get_effective_stat(self.atk, 'atk')

    @property
    def current_def_val(self):
        return self._get_effective_stat(self.def_val, 'def')

    @property
    def current_mag(self):
        return self._get_effective_stat(self.mag, 'mag')

    @property
    def current_res(self):
        return self._get_effective_stat(self.res, 'res')

    # NEW: Method called at the start of a character's turn
    def start_turn(self):
        # Process Damage Over Time (DOT) effects
        # It's safer to iterate over a copy if an effect could modify the list during iteration.
        # However, since duration decrement is in end_turn, a direct loop is generally fine here.
        # But using a copy for robustness:
        effects_to_process = list(self.active_status_effects) 
        for effect in effects_to_process:
            if effect.get("effect_type") == "dot":
                # Ensure it's a DOT effect and still has duration
                if "damage_per_turn" in effect and effect["duration"] > 0:
                    min_dmg, max_dmg = effect["damage_per_turn"]
                    damage = random.randint(min_dmg, max_dmg)
                    self.take_damage(damage) # Use existing take_damage method to apply health reduction

                    # --- IMPORTANT: How to display battle messages ---
                    # The `add_battle_message` function is likely in main.py.
                    # Directly importing `main` can sometimes lead to circular dependencies.
                    # If you encounter issues, you might need to refactor how messages are passed
                    # (e.g., return messages from start_turn, or pass a message queue object).
                    # For now, this direct import is a common workaround for smaller projects.
                    try:
                        import main # Attempt to import main to access add_battle_message
                        main.add_battle_message(f"{self.name} is {effect['name'].lower()} for {damage} damage!", (255, 100, 0)) # Orange color
                    except ImportError:
                        print(f"DEBUG: {self.name} is {effect['name'].lower()} for {damage} damage!") # Fallback print
            
        # You can add other turn-start effects here in the future

    # NEW: Method called at the end of a character's turn
    def end_turn(self):
        # Decrement duration for all active effects
        new_active_status_effects = []
        for effect in self.active_status_effects:
            effect['duration'] -= 1
            if effect['duration'] > 0:
                new_active_status_effects.append(effect)
            else:
                # Assuming `add_battle_message` is available via import or global scope
                # If not, you might need to return messages or pass battle_message_queue
                print(f"{self.name} is no longer {effect['name']}!") # Fallback print
                # import main # If add_battle_message needs to be imported, this is usually bad practice
                # main.add_battle_message(f"{self.name} is no longer {effect['name']}!", (200, 200, 200)) # Example
        self.active_status_effects = new_active_status_effects
        print(f"DEBUG: {self.name} active effects after end_turn: {self.active_status_effects}")

    def get_stats_lines(self):
        # Updated to display current effective stats
        lines = [
            f"HP: {self.current_hp}/{self.max_hp}",
            f"MP: {self.current_mp}/{self.max_mp}",
            f"ATK: {self.current_atk} (Base: {self.atk})",
            f"DEF: {self.current_def_val} (Base: {self.def_val})",
            f"MAG: {self.current_mag} (Base: {self.mag})",
            f"RES: {self.current_res} (Base: {self.res})"
        ]
        if self.active_status_effects:
            lines.append("--- Status Effects ---")
            for effect in self.active_status_effects:
                lines.append(f"{effect['name']} ({effect['duration']} turns left)")
        return lines