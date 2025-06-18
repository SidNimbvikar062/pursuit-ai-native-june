import datetime
import platform
import os

# --- Part 1: Determine the time-based greeting automatically ---
def get_time_of_day_greeting():
    """Determines the appropriate greeting based on the current hour."""
    current_hour = datetime.datetime.now().hour # Get the current hour (0-23)

    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

# --- Part 2: Get user inputs ---
def get_user_input(prompt):
    """Gets input from the user with a prompt."""
    return input(prompt).strip() # .strip() removes leading/trailing whitespace

# --- Part 3: Define the special name ---
# IMPORTANT: Change this to YOUR actual name!
SPECIAL_NAME = "Sid"

# --- Part 4: Combine all conditions and generate the personalized greeting ---
def create_welcome_message(name, topic):
    """
    Generates a personalized welcome message based on name, topic, and time of day.
    Includes a special greeting for a predefined name.
    """
    time_of_day_greeting = get_time_of_day_greeting()

    # Check for the special name (case-insensitive for robustness)
    if name.lower() == SPECIAL_NAME.lower():
        return f"Hey {name}! {time_of_day_greeting}! Welcome back!"
    else:
        # Provide a default topic if the user leaves it blank
        display_topic = topic if topic else "something fascinating"
        # Provide a default name if the user leaves it blank
        display_name = name if name else "a new friend"
        return f"{time_of_day_greeting}, I'm {display_name}, and I'm learning about {display_topic}."

def clear_console():
    """Clears the console screen based on the operating system."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def main():
    """Main function to run the welcome message application."""
    clear_console()
    print("--- Personalized Welcome Message Generator ---")
    print("----------------------------------------------\n")

    user_name = get_user_input("Please enter your name: ")
    user_topic = get_user_input("What are you learning about? ")

    # Generate and print the message
    message = create_welcome_message(user_name, user_topic)
    print(f"\nYour Personalized Message:\n>>> {message} <<<\n")
    print("----------------------------------------------")
    input("Press Enter to exit...") # Keep console open until user presses Enter

if __name__ == "__main__":
    main()

