import datetime # Import the datetime module to get the current time

# --- Part 1: Determine the time-based greeting automatically ---
current_hour = datetime.datetime.now().hour # Get the current hour (0-23)

time_of_day_greeting = ""
if current_hour < 12:
    time_of_day_greeting = "Good morning"
elif 12 <= current_hour < 18:
    time_of_day_greeting = "Good afternoon"
else:
    time_of_day_greeting = "Good evening"

# --- Part 2: Get user inputs ---
user_name = input("Please enter your name: ")
user_topic = input("What are you learning about? ") # New: Ask the user about their topic

# --- Part 3: Define the special name (you can change this!) ---
special_name = "Sid" # <--- IMPORTANT: Change this to YOUR actual name!

# --- Part 4: Combine all conditions and print the personalized greeting ---
if user_name == special_name:
    # Special greeting for the specific name, including time of day
    print(f"Hey {user_name}! {time_of_day_greeting}! Welcome back!")
else:
    # Regular greeting, including time of day and the user's topic
    print(f"{time_of_day_greeting}, I'm {user_name}, and I'm learning about {user_topic}")