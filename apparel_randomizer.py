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

# Function to load configuration from a JSON file
def load_config(config_filename):
    try:
        with open(config_filename, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Config file '{config_filename}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{config_filename}'. Please check the format.")
        exit(1)

# Load the configuration from the JSON file at the beginning of the script
config = load_config('config.json')

global last_selected, categories_order
last_selected = {}  # Dictionary to keep track of the last chosen item for each category
categories_order = list(config.keys())[3:]  # Initialize with categories
random.shuffle(categories_order)  # Shuffle the initial order

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
def overwrite_cfg(last_numbers, output_directory, output_filename):
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

    # Modify the first line
    lines[0] = f'rp setapparel {last_numbers}\n'

    # Write the modified lines back to the file
    with open(output_path, 'w') as file:
        file.writelines(lines)
    print(f"Selected Apparel: {name}")

# Function to press the F9 key
def press_f9_key():
    keyboard.press_and_release('F9')

# Function to run the main script
def run_script():
    global categories_order, last_selected, config

    # Extract configuration values
    output_directory = config['output_directory'] + '\\garrysmod\\cfg'
    output_filename = config['output_filename']
    time_delay_seconds = config['time_delay_seconds']

    while running_flag.is_set():
        if is_gmod_active():  # Check if GMod is the active window
            category = categories_order[0]
            checkbox_index = list(config.keys())[3:].index(category)
            if checkbox_vars[checkbox_index].get() == 0:
                categories_order.append(categories_order.pop(0))
                continue

            last_numbers = select_last_numbers_from_list(category)
            overwrite_cfg(last_numbers, output_directory, output_filename)
            press_f9_key()
            time.sleep(1)

            categories_order.append(categories_order.pop(0))

        time.sleep(time_delay_seconds)

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
        config[category] = selected_items
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)

        # Function to load text from a file
    def load_text_file(filename):
        try:
            with open(filename, 'r') as file:
                lines = file.read().splitlines()
            return lines
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
            exit(1)
    # Load the contents of the specified .txt file
    list_path = os.path.join(os.path.dirname(__file__), category + '.txt')
    lines = load_text_file(list_path)
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

# Function to update time_delay_seconds
def update_time_delay():
    global time_delay_seconds
    new_time_delay = int(time_delay_entry.get())
    time_delay_seconds = new_time_delay
    
    # Update the value in the config dictionary
    config['time_delay_seconds'] = new_time_delay
    
    # Save the updated config back to the JSON file
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

# Function to update output_directory
def update_output_directory():
    global output_directory
    new_output_directory = output_directory_entry.get()
    output_directory = new_output_directory
    
    # Update the value in the config dictionary
    config['output_directory'] = new_output_directory
    
    # Save the updated config back to the JSON file
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

# Set the geometry
root.geometry("400x285")

# Create and pack the start button
start_button = tk.Button(root, text="Start", command=start_script)
start_button.grid(row=0, column=0, padx=10, pady=5, sticky='w')

# Create and pack the stop button
stop_button = tk.Button(root, text="Stop", command=stop_script)
stop_button.grid(row=0, column=1, padx=10, pady=5, sticky='w')

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