import tkinter as tk
from tkinter import messagebox
import datetime
import platform
import os
from PIL import Image, ImageTk

# --- Constants for Styling ---
BG_COLOR = "#000000"           # Black background for content frame
FG_COLOR = "#FFFFFF"           # White foreground text
ACCENT_COLOR = "#DC2626"       # Red accent color (Tailwind red-600)
ACCENT_DARK = "#B91C1C"        # Darker red for active states (Tailwind red-700)
FONT_FAMILY = "Inter"          # Using a common sans-serif font
LARGE_FONT_SIZE = 18
MEDIUM_FONT_SIZE = 12
SMALL_FONT_SIZE = 10

# --- Image Path ---
# IMPORTANT: Change this to the actual path of your background image file.
# Make sure this image file is in the same directory as your Python script.
IMAGE_PATH = "p5stars.png" # Updated to your specified image name

# --- Core Logic Functions (Reused from previous Python script) ---

# IMPORTANT: Change this to YOUR actual name!
SPECIAL_NAME = "Sid"

def get_time_of_day_greeting():
    """Determines the appropriate greeting based on the current hour."""
    current_hour = datetime.datetime.now().hour # Get the current hour (0-23)

    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

def create_welcome_message(name, topic):
    """
    Generates a personalized welcome message based on name, topic, and time of day.
    Includes a special greeting for a predefined name.
    """
    time_of_day_greeting = get_time_of_day_greeting()

    # Trim whitespace from inputs for cleaner processing
    trimmed_name = name.strip()
    trimmed_topic = topic.strip()

    # Check for the special name (case-insensitive for robustness)
    if trimmed_name.lower() == SPECIAL_NAME.lower():
        return f"Hey {trimmed_name}! {time_of_day_greeting}! Welcome back!"
    else:
        # Provide a default topic if the user leaves it blank
        display_topic = trimmed_topic if trimmed_topic else "something fascinating"
        # Provide a default name if the user leaves it blank
        display_name = trimmed_name if trimmed_name else "a new friend"
        return f"{time_of_day_greeting}, I'm {display_name}, and I'm learning about {display_topic}."

# --- Tkinter UI Setup ---

class WelcomeApp:
    def __init__(self, master):
        self.master = master
        master.title("Personalized Welcome App")
        
        # Initial window size - Increased again for better overall fit and message box
        self.initial_width = 850
        self.initial_height = 650
        master.geometry(f"{self.initial_width}x{self.initial_height}")
        master.resizable(True, True) # Allow resizing for background image adjustment
        
        # Set minimum size to ensure it doesn't get too small for the layout/image
        master.minsize(self.initial_width, self.initial_height)


        # --- Load and set background image ---
        self.bg_image_original = None
        self.bg_photo = None
        try:
            # Get the directory of the script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the full path to the image
            full_image_path = os.path.join(script_dir, IMAGE_PATH)

            self.bg_image_original = Image.open(full_image_path)
            
            # Create a label to hold the background image, but don't place it yet.
            # Placement will be handled by on_resize to ensure correct sizing from start.
            self.bg_label = tk.Label(master)
            
            # Bind window resize event to update background image
            master.bind('<Configure>', self.on_resize)
            
        except FileNotFoundError:
            messagebox.showerror("Image Error", f"Background image not found at: {full_image_path}\n"
                                             "Please ensure the image file is in the same directory as the script or update IMAGE_PATH.")
            master.configure(bg="#1a1a1a") # Fallback dark background if image not found
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load background image: {e}")
            master.configure(bg="#1a1a1a") # Fallback dark background

        # --- Main content frame to hold all UI elements on top of the image ---
        # Using a slightly transparent black for the content frame makes text readable
        # while still allowing the background image to show through subtly.
        self.content_frame = tk.Frame(master, bg=BG_COLOR, bd=5, relief="flat", highlightbackground=ACCENT_COLOR, highlightthickness=1)
        # Place the content frame in the center, taking up more relative space
        self.content_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.9, relheight=0.9) # Increased relwidth/relheight

        # Bind configure event for content_frame to update wraplength
        self.content_frame.bind('<Configure>', self.update_wraplength)


        # --- Styling for widgets within the content frame ---
        # Labels
        tk.Label(self.content_frame, text="Welcome Message Generator",
                 bg=BG_COLOR, fg=ACCENT_COLOR,
                 font=(FONT_FAMILY, LARGE_FONT_SIZE, "bold")).pack(pady=15)

        tk.Label(self.content_frame, text="Enter your details to get a personalized greeting.",
                 bg=BG_COLOR, fg=FG_COLOR,
                 font=(FONT_FAMILY, SMALL_FONT_SIZE)).pack(pady=(0, 20))

        # --- Name Input ---
        tk.Label(self.content_frame, text="Your Name:",
                 bg=BG_COLOR, fg=FG_COLOR,
                 font=(FONT_FAMILY, MEDIUM_FONT_SIZE)).pack(anchor='w', padx=40) # Increased padx
        
        self.name_entry = tk.Entry(self.content_frame, width=40,
                                   bg="#333333", fg=FG_COLOR, insertbackground=ACCENT_COLOR, # Cursor color
                                   font=(FONT_FAMILY, MEDIUM_FONT_SIZE),
                                   relief="flat", bd=2, highlightbackground=ACCENT_COLOR, highlightthickness=1)
        self.name_entry.pack(pady=5, padx=40, fill='x') # Increased padx, fill='x'
        self.name_entry.bind("<Return>", self.generate_message_event) # Bind Enter key
        
        tk.Label(self.content_frame, text=f"Hint: Try typing \"{SPECIAL_NAME}\" for a special greeting!",
                 bg=BG_COLOR, fg="#888888",
                 font=(FONT_FAMILY, SMALL_FONT_SIZE - 2)).pack(anchor='w', padx=40) # Increased padx


        # --- Topic Input ---
        tk.Label(self.content_frame, text="What are you learning about?",
                 bg=BG_COLOR, fg=FG_COLOR,
                 font=(FONT_FAMILY, MEDIUM_FONT_SIZE)).pack(anchor='w', padx=40, pady=(15, 0)) # Increased padx
        
        self.topic_entry = tk.Entry(self.content_frame, width=40,
                                    bg="#333333", fg=FG_COLOR, insertbackground=ACCENT_COLOR,
                                    font=(FONT_FAMILY, MEDIUM_FONT_SIZE),
                                    relief="flat", bd=2, highlightbackground=ACCENT_COLOR, highlightthickness=1)
        self.topic_entry.pack(pady=5, padx=40, fill='x') # Increased padx, fill='x'
        self.topic_entry.bind("<Return>", self.generate_message_event) # Bind Enter key

        # --- Generate Button ---
        self.generate_button = tk.Button(self.content_frame, text="Generate Welcome Message",
                                         command=self.generate_message,
                                         bg=ACCENT_COLOR, fg=FG_COLOR,
                                         font=(FONT_FAMILY, MEDIUM_FONT_SIZE, "bold"),
                                         relief="raised", bd=0, padx=10, pady=8,
                                         activebackground=ACCENT_DARK, activeforeground=FG_COLOR,
                                         cursor="hand2") # Change cursor on hover
        self.generate_button.pack(pady=20, padx=40, fill='x') # Increased padx

        # --- Output Display ---
        tk.Label(self.content_frame, text="Your Personalized Message:",
                 bg=BG_COLOR, fg=FG_COLOR,
                 font=(FONT_FAMILY, MEDIUM_FONT_SIZE)).pack(anchor='w', padx=40, pady=(0, 5)) # Increased padx
        
        self.output_label = tk.Label(self.content_frame, text="Your message will appear here...",
                                      bg="#1a1a1a", fg="#AAAAAA", # Slightly lighter black for output box
                                      font=(FONT_FAMILY, MEDIUM_FONT_SIZE),
                                      justify="center", # Center text
                                      relief="solid", bd=1, highlightbackground=ACCENT_COLOR, highlightthickness=1,
                                      padx=20, pady=20) # Increased internal padding for MORE space
        self.output_label.pack(pady=5, padx=40, fill='both', expand=True) # Increased padx, fill='both', expand=True

        # Ensure initial sizing and wraplength are correct after all widgets are packed.
        # This is crucial for getting correct initial winfo_width/height.
        self.master.update_idletasks()
        if self.bg_image_original: # Only call if image was loaded successfully
            self.on_resize(None) # Call once to set initial image size correctly
        self.update_wraplength(None) # Call once to set initial wraplength correctly


        # Initial message display
        self.generate_message()


    def on_resize(self, event):
        """Resizes the background image to COVER the window, maintaining aspect ratio.
           Might crop parts of the image if aspect ratios don't match."""
        if self.bg_image_original:
            new_width = self.master.winfo_width()
            new_height = self.master.winfo_height()

            # Crucial check: only proceed if dimensions are valid (not 0)
            if new_width <= 0 or new_height <= 0:
                return

            img_width, img_height = self.bg_image_original.size
            
            # Calculate ratio to scale the image to cover the new window size
            ratio_width = new_width / img_width
            ratio_height = new_height / img_height

            # Choose the larger ratio to ensure the image covers the entire area
            scale_ratio = max(ratio_width, ratio_height)

            # Calculate new dimensions for the image
            resized_width = int(img_width * scale_ratio)
            resized_height = int(img_height * scale_ratio)

            # Resize the image using high-quality resampling
            resized_image = self.bg_image_original.resize((resized_width, resized_height), Image.Resampling.LANCZOS)
            
            # Crop the image to the exact window dimensions if it's larger
            # This ensures the image perfectly fills the window without distortion or empty space.
            x_offset = (resized_width - new_width) // 2
            y_offset = (resized_height - new_height) // 2
            cropped_image = resized_image.crop((x_offset, y_offset, x_offset + new_width, y_offset + new_height))

            self.bg_photo = ImageTk.PhotoImage(cropped_image)
            self.bg_label.config(image=self.bg_photo)
            # Explicitly place the background label with the exact new dimensions
            # and send it to the back to ensure other widgets are on top.
            self.bg_label.place(x=0, y=0, width=new_width, height=new_height)
            self.bg_label.lower() # Ensure it's behind other widgets

    def update_wraplength(self, event):
        """Updates the wraplength of the output label based on content frame width."""
        # Get the current width of the content frame
        frame_width = self.content_frame.winfo_width()
        if frame_width > 0:
            # Set wraplength to a percentage of the frame width, considering the output_label's internal padding.
            effective_width = frame_width - (self.output_label.cget('padx') * 2) 
            # Ensure wraplength is at least 1 to prevent errors with very small widths.
            self.output_label.config(wraplength=max(1, effective_width))


    def generate_message(self):
        """Fetches input, generates message, and updates the output label."""
        name = self.name_entry.get()
        topic = self.topic_entry.get()
        
        # Simulate a slight delay for "generating" effect
        self.output_label.config(text="Generating...", fg=ACCENT_COLOR)
        self.master.update_idletasks() # Force update the GUI immediately

        # Use after() to create a small delay before the actual message appears
        self.master.after(500, lambda: self._update_message(name, topic))

    def _update_message(self, name, topic):
        """Helper function to update the message after a delay."""
        message = create_welcome_message(name, topic)
        self.output_label.config(text=message, fg=FG_COLOR) # Set back to white after generation

    def generate_message_event(self, event):
        """Event handler for Enter key press."""
        self.generate_message()

# --- Main Application Execution ---
if __name__ == "__main__":
    # Ensure Pillow is installed
    try:
        from PIL import Image, ImageTk
    except ImportError:
        messagebox.showerror("Error", "Pillow library not found.\nPlease install it using: pip install Pillow")
        exit()

    root = tk.Tk()
    app = WelcomeApp(root)
    root.mainloop()
