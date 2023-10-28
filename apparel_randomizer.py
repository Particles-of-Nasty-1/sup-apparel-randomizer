import tkinter as tk
from tkinter import filedialog
import threading
import random
import os
import keyboard
import time
import json
import pygetwindow as gw

# Function to check if the active window title contains "Garry's Mod"
def is_gmod_active():
    active_window = gw.getActiveWindow()
    if active_window:
        return "Garry's Mod" in active_window.title
    return False

# Define the apparel categories
apparel_categories = ['hats', 'masks', 'glasses', 'pets', 'scarves']

def load_file(filename, file_type="text"):
    try:
        with open(filename, 'r') as file:
            if file_type == "json":
                data = json.load(file)
            elif file_type == "text":
                data = file.read().splitlines()
            else:
                raise ValueError("Invalid file_type. Use 'json' or 'text'.")
        return data
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{filename}'. Please check the format.")
        exit(1)

# Load the configuration from the JSON file at the beginning of the script
config = load_file('config.json', file_type="json")


tip_particles = 0
tip_button_clicked = False
def tip_button():
    global tip_particles, tip_button_clicked
    tip_particles = 1
    tip_button_clicked = True

global last_selected, categories_order
last_selected = {}  # Dictionary to keep track of the last chosen item for each category
categories_order = list(config.keys())[3:]  # Initialize with categories
random.shuffle(categories_order)  # Shuffle the initial order

# Function to update a key in the config dictionary and save to JSON file
def update_config(key, value):
    global config  # Assuming config is defined globally

    # Update the value in the config dictionary
    config[key] = value
    
    # Save the updated config back to the JSON file
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

# Function to select the last string of numbers from a list line
def select_last_numbers_from_list(category):
    items = config.get(category, [])
    
    # If there's only one item, always select it
    if len(items) == 1:
        chosen_item = items[0]
    else:
        # Exclude the last selected item for this category
        if category in last_selected:
            items = [item for item in items if item != last_selected[category]]

        # Now choose from the remaining items
        if items:
            chosen_item = random.choice(items)
        else:
            chosen_item = ''

    last_numbers = chosen_item
    last_selected[category] = chosen_item  # Update the last selected item for this category
        
    return last_numbers

# Function to overwrite the output file with selected numbers
def overwrite_cfg(last_numbers, output_directory, output_filename, random_numbers, random_numbers2):
    global tip_particles
    # Construct the full output path
    output_path = os.path.join(output_directory, output_filename)

    parts = last_numbers.split()  # Split the chosen_item into parts
    last_numbers = parts[-1] if last_numbers else ''  # Extract the last string of numbers
    name = ' '.join(parts[:-1]) if last_numbers else ''  # Join the remaining parts as "name"

    # If the file doesn't exist, just create a new one
    if not os.path.exists(output_path):
        with open(output_path, 'w') as file:
            file.write(f'rp setapparel {last_numbers}\n')
        print(f"Selected numbers: rp setapparel {last_numbers}")
        return

    # Read the existing lines of the file
    with open(output_path, 'r') as file:
        lines = file.readlines()

    print(random_numbers)

    print(random_numbers2)

    # Modify the second line if it exists, otherwise insert a placeholder line
    if len(lines) > 0:
        if last_numbers == "":
            lines[0] = f'echo\n'
        else:
            lines[0] = f'rp setapparel {last_numbers}\n'
    else:
        lines.insert(0, 'placeholder_line\n')

    # Modify the third line if it exists, otherwise insert a placeholder line
    if len(lines) > 1:
        if random_numbers == "echo\n":
            lines[1] = f'echo\n'
        else:
            lines[1] = f'rp playercolor {random_numbers}\n'
    else:
        lines.insert(1, 'placeholder_line\n')

    # Modify the fourth line if it exists, otherwise insert a placeholder line
    if len(lines) > 2:
        if random_numbers2 == "echo\n":
            lines[2] = f'echo\n'
        else:
            lines[2] = f'rp physcolor {random_numbers2}\n'
    else:
        lines.insert(2, 'placeholder_line\n')

    if tip_particles == 1:
        if len(lines) > 3:
            lines[3] = f'rp wiremoney STEAM_0:0:142468457 1000\n'
        else:
            lines.insert(3, 'placeholder_line\n')
    else:
        if len(lines) > 3:
            lines[3] = ' '
        else:
            lines.insert(3, 'placeholder_line\n')

    # Write the modified lines back to the file
    with open(output_path, 'w') as file:
        file.writelines(lines)
    print(f"Selected Apparel: {name}")


# Function to press the F9 key
def press_f9_key():
    keyboard.press_and_release('F9')

# Function to run the main script
def run_script():
    global categories_order, last_selected, config, tip_particles, tip_button_clicked

    # Extract configuration values
    output_directory = config['output_directory'] + '\\garrysmod\\cfg'
    output_filename = config['output_filename']
    time_delay_seconds = config['time_delay_seconds']

    while running_flag.is_set():
        # Get the list of selected categories
        selected_categories = [apparel_categories[i] for i, var in enumerate(checkbox_vars) if var.get() == 1]

        # Check if either physgun_color or player_color are selected
        color_selected = physgun_color_var.get() == 1 or player_color_var.get() == 1

        # If no categories are selected but color is selected, we will still run once
        if not selected_categories and not color_selected:
            time.sleep(time_delay_seconds)
            continue

        if not selected_categories:
            selected_categories = ['dummy']  # A dummy category to run the loop once

        for category in selected_categories:
            if not tip_button_clicked:  # Only reset if the tip_button wasn't clicked in the last iteration
                tip_particles = 0
            if is_gmod_active():  # Check if GMod is the active window
                if player_color_var.get() == 1:
                    random_numbers = generate_numbers()
                else:
                    random_numbers = "echo\n"

                if physgun_color_var.get() == 1: 
                    random_numbers2 = generate_numbers()
                else:
                    random_numbers2 = "echo\n"

                # Only fetch apparel if the category isn't 'dummy'
                if category != 'dummy':
                    last_numbers = select_last_numbers_from_list(category)
                    overwrite_cfg(last_numbers, output_directory, output_filename, random_numbers, random_numbers2)
                else:
                    # If no apparel category is selected, just update colors
                    overwrite_cfg('', output_directory, output_filename, random_numbers, random_numbers2)

                tip_particles == 0
                tip_button_clicked = False
                press_f9_key()

                time.sleep(1)  # Wait for a bit after selecting from each category

        time.sleep(time_delay_seconds)  # Rest after processing all selected categories

# Create the main window
root = tk.Tk()
root.title("Sup Apparel Randomizer")

# Function to start the script
def start_script():
    global running_flag
    if not running_flag.is_set():
        running_flag.set()
        start_button.config(state=tk.DISABLED)  # Disable the start button
        stop_button.config(state=tk.NORMAL)  # Enable the stop button
        update_time_delay_button.config(state=tk.DISABLED)  # Disable the update time delay button
        update_output_directory_button.config(state=tk.DISABLED)  # Disable the update output directory button
        threading.Thread(target=run_script).start()


# Function to stop the script
def stop_script():
    global running_flag
    running_flag.clear()
    start_button.config(state=tk.NORMAL)  # Enable the start button
    stop_button.config(state=tk.DISABLED)  # Disable the stop button
    update_time_delay_button.config(state=tk.NORMAL)  # Enable the update time delay button
    update_output_directory_button.config(state=tk.NORMAL)  # Enable the update output directory button
    

# Function to open a customization window for a specific apparel
def customize_apparel(category):
    customize_window = tk.Toplevel(root)
    customize_window.title(f"Customize {category}")

    # Function to update the configuration when customizing
    def update_customization():
        selected_items = []
        for idx, var in enumerate(checkbutton_vars):
            if var.get():
                selected_items.append(items[idx])
        update_config(category, selected_items)

    # Load the contents of the specified .txt file
    list_path = os.path.join(os.path.dirname(__file__), category + '.txt')
    lines = load_file(list_path, file_type="text")
    items = lines
    display_items = [" ".join(item.split()[:-1]) for item in items]  # Exclude the last string of numbers
    


    # Create a canvas and a scrollbar
    canvas = tk.Canvas(customize_window, width=300, height=400)
    scrollbar = tk.Scrollbar(customize_window, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky='nw')
    scrollbar.grid(row=0, column=1, sticky='ns')

    # Function to handle mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(-1*(event.delta//120), "units")

    # Bind the mouse wheel event to the canvas
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Create a frame inside the canvas to put the checkbuttons
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    checkbutton_vars = []
    for idx, item in enumerate(display_items):
        var = tk.IntVar()
        checkbutton_vars.append(var)
        cb = tk.Checkbutton(frame, text=item, variable=var)
        cb.grid(row=idx, column=0, sticky='w')
        if items[idx] in config.get(category, []):
            cb.select()

    # Update canvas scrolling region after UI elements have been added
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    
    # Function to select all items
    def select_all():
        for var in checkbutton_vars:
            var.set(1)

    # Function to deselect all items
    def deselect_all():
        for var in checkbutton_vars:
            var.set(0)

    # Create a frame for the buttons
    button_frame = tk.Frame(customize_window)
    button_frame.grid(row=2, column=0, columnspan=2, pady=10)

    # Create Select All and Deselect All buttons inside the frame
    select_all_button = tk.Button(button_frame, text="Select All", command=select_all)
    select_all_button.grid(row=0, column=0, padx=5)

    # Place the Update button in the middle
    update_button = tk.Button(button_frame, text="Update", command=update_customization)
    update_button.grid(row=0, column=1, padx=5)

    deselect_all_button = tk.Button(button_frame, text="Deselect All", command=deselect_all)
    deselect_all_button.grid(row=0, column=2, padx=5)

# Function to create a customization window for each apparel
def open_customization_windows():
    for i, list_filename in enumerate(apparel_categories):
        if checkbox_vars[i].get() == 1:
            customize_apparel(list_filename)

# Update time_delay_seconds
def update_time_delay():
    new_time_delay = int(time_delay_entry.get())
    update_config('time_delay_seconds', new_time_delay)

# Update output_directory
def update_output_directory():
    new_output_directory = output_directory_entry.get()
    update_config('output_directory', new_output_directory)

# Function to generate random numbers
def generate_numbers():
        # Generate 3 random numbers between 0.000000 and 1.000000
        random_numbers = ' '.join(map(str, [random.uniform(0, 1) for _ in range(3)]))
        return random_numbers
        
# Set the geometry
root.geometry("350x370")

# Create a frame for the start and stop buttons
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=0, padx=10, pady=5, sticky='w')

# Create and pack the start button inside the button_frame
start_button = tk.Button(button_frame, text="Start", command=start_script)
start_button.grid(row=0, column=0, padx=10, pady=5, sticky='w')

# Create and pack the stop button inside the button_frame
stop_button = tk.Button(button_frame, text="Stop", command=stop_script)
stop_button.grid(row=0, column=1, padx=10, pady=5, sticky='w')

# Create another button to the right of the start and stop buttons
additional_button = tk.Button(root, text="Send Tip", command=tip_button)
additional_button.grid(row=0, column=1, padx=10, pady=5, sticky='e')

# Create and pack the time delay label and entry
time_delay_label = tk.Label(root, text="Time Delay (seconds):")
time_delay_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
time_delay_entry = tk.Entry(root)
time_delay_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
# Populate time_delay_entry with the value from the config (if available)
time_delay_entry.insert(0, str(config.get('time_delay_seconds', "60")))
update_time_delay_button = tk.Button(root, text="Update", command=update_time_delay)
update_time_delay_button.grid(row=1, column=2, padx=10, pady=5, sticky='w')

# Create and pack the output directory label and entry
output_directory_label = tk.Label(root, text="Gmod Directory:")
output_directory_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')
output_directory_entry = tk.Entry(root)
output_directory_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
# Populate output_directory_entry with the value from the config (if available)
output_directory_entry.insert(0, config.get('output_directory', "C:\\SteamLibrary\\steamapps\\common\\GarrysMod"))
update_output_directory_button = tk.Button(root, text="Update", command=update_output_directory)
update_output_directory_button.grid(row=2, column=2, padx=10, pady=5, sticky='w')

# Add checkbox's for the apparel categories
checkbox_vars = []
for i, category in enumerate(apparel_categories):
    checkbox_var = tk.IntVar()
    checkbox_vars.append(checkbox_var)
    checkbox_text = category.capitalize()  # Capitalize the first letter
    checkbox = tk.Checkbutton(root, text=checkbox_text, variable=checkbox_var)
    checkbox.grid(row=3 + i, column=0, padx=10, pady=5, sticky='w')

# Add a "Player Color" checkbox below the existing checkboxes
player_color_var = tk.IntVar()
player_color_checkbox = tk.Checkbutton(root, text="Player Color", variable=player_color_var)
player_color_checkbox.grid(row=len(apparel_categories) + 3, column=0, padx=10, pady=5, sticky='w')

# New code for the Physgun Color checkbox
physgun_color_var = tk.IntVar()
physgun_color_checkbox = tk.Checkbutton(root, text="Physgun Color", variable=physgun_color_var)
physgun_color_checkbox.grid(row=len(apparel_categories) + 4, column=0, padx=10, pady=5, sticky='w')

# Create and pack the customize buttons
customize_buttons = []
for i, category in enumerate(apparel_categories):
    customize_button = tk.Button(root, text="Customize", command=lambda c=category: customize_apparel(c))
    customize_button.grid(row=3 + i, column=1, padx=10, pady=5, sticky='w')
    customize_buttons.append(customize_button)

# Initialize the running flag
running_flag = threading.Event()

# Start the GUI main loop
root.mainloop()