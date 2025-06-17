# First, let's get the user's name as input
user_name = input("Please enter your name: ")

# Define the topic
topic = "AI"

# Define the special name you're looking for
special_name = "Sid" # <--- IMPORTANT: Change this to YOUR actual name!

# Now, we use an 'if' statement to check for the special name
if user_name == special_name:
    print(f"Hey, it's the awesome AI Director, {user_name}!")
else:
    print(f"Hello, I'm {user_name}, and I'm learning about {topic}")