import random

class Move:
    def __init__(self, name, accuracy, damage_range, type, cost, speed=99, status_effect_data=None, heal_range=None, target="enemy"): # ADDED 'target="enemy"'
        self.name = name
        self.accuracy = accuracy # 0-100
        self.damage_range = damage_range # [min, max]
        self.type = type # "physical", "magic", "status", "heal"
        self.cost = cost # MP cost
        self.speed = speed # Lower is faster (initiative)

        self.status_effect_data = status_effect_data 
        self.heal_range = heal_range
        self.target = target # NEW: "enemy" or "self" for status/heal moves


    def calculate_damage(self, attacker, defender):
        # Moves of type "status" or "heal" do not deal damage
        if self.type == "status" or self.type == "heal":
            return None # Indicate no damage calculation is needed

        if random.randint(1, 100) > self.accuracy:
            return "miss"

        # Base damage is a random value within the move's damage range
        base_damage = random.randint(self.damage_range[0], self.damage_range[1])

        # Apply attacker's stat
        if self.type == "physical":
            modified_damage = base_damage + attacker.current_atk # Use current_atk
        elif self.type == "magic":
            modified_damage = base_damage + attacker.current_mag # Use current_mag
        else:
            modified_damage = base_damage # Should not happen for physical/magic types

        # Apply defender's stat
        if self.type == "physical":
            final_damage = max(1, modified_damage - defender.current_def_val) # Use current_def_val
        elif self.type == "magic":
            final_damage = max(1, modified_damage - defender.current_res) # Use current_res
        else:
            final_damage = max(1, modified_damage) # Should not happen

        # Critical Hit Chance (e.g., 15% chance for a critical hit)
        is_critical = False
        if random.randint(1, 100) <= 15: # 15% chance
            final_damage = int(final_damage * 1.5) # 1.5x damage for critical hit
            is_critical = True

        return final_damage, is_critical