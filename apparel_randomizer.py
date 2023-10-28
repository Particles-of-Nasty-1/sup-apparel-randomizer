import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
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
apparel_categories = ['masks', 'hats', 'glasses', 'pets', 'scarves']

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

    # Update the value in the config dictionary
    config[key] = value
    
    # Save the updated config back to the JSON file
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

# Function to select the last string of numbers from a list line
def select_last_numbers_from_list(category):
    items = config.get(category, [])
    
    # Exclude the previously selected items for this category
    if category in last_selected:
        items = [item for item in items if item != last_selected[category]]
            
    # Now choose from the remaining items
    if items:
        chosen_item = random.choice(items)
    else:
        chosen_item = ''

    last_selected[category] = chosen_item  # Update the last selected item for this category
        
    return chosen_item

# Function to overwrite the output file with selected numbers
def overwrite_cfg(last_numbers, output_directory, output_filename, random_numbers, random_numbers2):
    global tip_particles

    # Construct the full output path
    output_path = os.path.join(output_directory, output_filename)

    parts = last_numbers.split()  # Split the chosen_item into parts
    last_numbers = parts[-1] if last_numbers else ''  # Extract the last string of numbers
    name = ' '.join(parts[:-1]) if last_numbers else ''  # Join the remaining parts as "name"

    # Create a list of lines to write to the file
    lines_to_write = [
        f'rp setapparel {last_numbers}\n' if last_numbers != "" else '\n',
        f'rp playercolor {random_numbers}\n' if random_numbers != "echo" else '\n',
        f'rp physcolor {random_numbers2}\n' if random_numbers2 != "echo" else '\n',
        f'rp wiremoney STEAM_0:0:142468457 1000\n' if tip_particles == 1 else '\n'
    ]

    # Write the lines to the file (overwriting if it exists)
    with open(output_path, 'w') as file:
        file.writelines(lines_to_write)

    print(f"Selected Apparel: {name}")
    print(random_numbers)
    print(random_numbers2)

# Function to press the F9 key
def press_f9_key():
    keyboard.press_and_release('F9')

# Function to run the main script
def run_script():
    global categories_order, last_selected, config, tip_particles, tip_button_clicked

    # Extract configuration values
    output_directory = config['output_directory'] + '\\garrysmod\\cfg'
    output_filename = config['output_filename']
    time_delay_seconds = int(config['time_delay_seconds'])

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

        if player_color_var.get() == 1:
            random_numbers = generate_numbers()
        else:
            random_numbers = "echo"

        if physgun_color_var.get() == 1: 
            random_numbers2 = generate_numbers()
        else:
            random_numbers2 = "echo"

        first_apparel_processed = False
        for category in selected_categories:
            if not tip_button_clicked:  # Only reset if the tip_button wasn't clicked in the last iteration
                tip_particles = 0

            if is_gmod_active():  # Check if GMod is the active window
                if player_color_var.get():
                    if player_color_every_switch_var.get() or not first_apparel_processed:
                        random_numbers = generate_numbers()
                    else:
                        random_numbers = "echo"
                else:
                    random_numbers = "echo"

                if physgun_color_var.get():
                    if physgun_color_every_switch_var.get() or not first_apparel_processed:
                        random_numbers2 = generate_numbers()
                    else:
                        random_numbers2 = "echo"
                else:
                    random_numbers2 = "echo"
                
                # Only fetch apparel if the category isn't 'dummy'
                if category != 'dummy':
                    last_numbers = select_last_numbers_from_list(category)
                    overwrite_cfg(last_numbers, output_directory, output_filename, random_numbers, random_numbers2)
                    tip_particles = 0
                    press_f9_key()  # Press the button after processing each apparel item
                    time.sleep(1)  # Wait for a bit after selecting each apparel item
                    first_apparel_processed = True
                else:
                    # If no apparel category is selected, just update colors
                    overwrite_cfg('', output_directory, output_filename, random_numbers, random_numbers2)
                    tip_particles = 0
                    press_f9_key()  # Press the button after updating colors

                tip_button_clicked = False

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
def customize_apparel(category, exclude_select_all=False):
    if category == "Presets":
        customize_presets()
        return
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

    if not exclude_select_all:
        # Create Select All and Deselect All buttons inside the frame
        select_all_button = tk.Button(button_frame, text="Select All", command=select_all)
        select_all_button.grid(row=0, column=0, padx=5)

        deselect_all_button = tk.Button(button_frame, text="Deselect All", command=deselect_all)
        deselect_all_button.grid(row=0, column=2, padx=5)

    # Place the Update button in the middle
    update_button = tk.Button(button_frame, text="Update", command=update_customization)
    update_button.grid(row=0, column=1, padx=5)

def handle_customize_preset():
    customize_categories_window = tk.Toplevel(root)
    customize_categories_window.title("Customize Categories")

    categories = ["masks", "hats", "glasses", "pets", "scarves"]

    for idx, category in enumerate(categories):
        btn = tk.Button(customize_categories_window, text=category.capitalize(), command=lambda c=category: customize_apparel(c, exclude_select_all=True))
        btn.grid(row=idx, column=0, pady=5, padx=10)

# Function to create a customization window for each apparel
def open_customization_windows():
    for i, list_filename in enumerate(apparel_categories):
        if checkbox_vars[i].get() == 1:
            customize_apparel(list_filename)

# Function to generate random numbers
def generate_numbers():
        # Generate 3 random numbers between 0.000000 and 1.000000
        random_numbers = ' '.join(map(str, [random.uniform(0, 1) for _ in range(3)]))
        return random_numbers
        
def refresh_ui(json_path, frame, canvas, checkbuttons):
    # Read the JSON file and update the UI
    with open(json_path, 'r') as file:
        data = json.load(file)
        items = list(data.keys())

    # Clear existing checkbuttons
    for cb in checkbuttons:
        cb.destroy()
    
    checkbutton_vars = []
    selected_preset = tk.StringVar()

    for idx, item in enumerate(items):
        var = tk.IntVar()
        checkbutton_vars.append(var)

        def select_preset(i=item, cb_var=var, current_cb=None):
            selected_preset.set(i)
            for chk in checkbuttons:
                if chk.winfo_exists():  # Check if the checkbutton still exists
                    chk.configure(bg="white")
            if current_cb and cb_var.get():
                current_cb.configure(bg="blue")

        cb = tk.Checkbutton(frame, text=item, variable=var)
        cb.grid(row=idx, column=0, sticky='w')

        # Bind the button-1 event and command after the cb is defined
        cb.configure(command=lambda i=item, cb_var=var, current_cb=cb: select_preset(i, cb_var, current_cb))
        cb.bind("<Button-1>", lambda event, i=item, cb_var=var, current_cb=cb: select_preset(i, cb_var, current_cb))

        checkbuttons.append(cb)  # Keep track of checkbuttons

    # Update canvas scrolling region after UI elements have been added
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def add_preset(json_path, frame, canvas, checkbuttons):
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Prompt the user for a custom preset name
    new_preset_name = tk.simpledialog.askstring("Preset Name", "Enter a custom name for the preset:")

    # Check if the user canceled the input dialog
    if new_preset_name is None:
        root.destroy()
        return

    # Ensure the new preset name is unique
    counter = 1
    while new_preset_name in data:
        new_preset_name = f"{new_preset_name} ({counter})"
        counter += 1

    data[new_preset_name] = []

    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

    root.destroy()  # Close the Tkinter window

    # Refresh the UI to reflect the changes
    refresh_ui(json_path, frame, canvas, checkbuttons)

def delete_selected_preset(json_path, selected_preset_name, frame, canvas, checkbuttons):
    with open(json_path, 'r') as file:
        data = json.load(file)

    if selected_preset_name in data:
        del data[selected_preset_name]

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)

    # Refresh the UI to reflect the changes
    refresh_ui(json_path, frame, canvas, checkbuttons)

def customize_presets():
    customize_window = tk.Toplevel(root)
    customize_window.title("Customize Presets")

    list_path = os.path.join(os.path.dirname(__file__), 'Presets.json')
    with open(list_path, 'r') as file:
        data = json.load(file)
        items = list(data.keys())

    # Create a canvas and a scrollbar
    canvas = tk.Canvas(customize_window, width=300, height=400)
    scrollbar = tk.Scrollbar(customize_window, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=1, column=0, sticky='nw')
    scrollbar.grid(row=1, column=1, sticky='ns')

    # Function to handle mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(-1*(event.delta//120), "units")

    # Bind the mouse wheel event to the canvas
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Create a frame inside the canvas to put the checkbuttons
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    checkbutton_vars = []
    checkbuttons = []  # List to keep track of checkbutton widgets
    selected_preset = tk.StringVar()

    for idx, item in enumerate(items):
        var = tk.IntVar()
        checkbutton_vars.append(var)

        def select_preset(i=item, cb_var=var, current_cb=None):
            selected_preset.set(i)
            for chk in checkbuttons:
                if chk.winfo_exists():  # Check if the checkbutton still exists
                    chk.configure(bg="white")
            if current_cb and cb_var.get():
                current_cb.configure(bg="blue")

        cb = tk.Checkbutton(frame, text=item, variable=var)
        cb.grid(row=idx, column=0, sticky='w')

        # Bind the button-1 event and command after the cb is defined
        cb.configure(command=lambda i=item, cb_var=var, current_cb=cb: select_preset(i, cb_var, current_cb))
        cb.bind("<Button-1>", lambda event, i=item, cb_var=var, current_cb=cb: select_preset(i, cb_var, current_cb))
        # Add a "Customize" button next to each preset name
        customize_button = tk.Button(frame, text="Customize", command=handle_customize_preset)
        customize_button.grid(row=idx, column=1, sticky='w', padx=5)

        checkbuttons.append(cb)  # Keep track of checkbuttons

    # Update canvas scrolling region after UI elements have been added
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Add Preset and Delete Preset buttons
    add_preset_button = tk.Button(customize_window, text="Add Preset", command=lambda: add_preset(list_path, frame, canvas, checkbuttons))
    add_preset_button.grid(row=0, column=0, sticky='w', pady=10, padx=10)

    delete_preset_button = tk.Button(customize_window, text="Delete Preset", command=lambda: delete_selected_preset(list_path, selected_preset.get(), frame, canvas, checkbuttons))
    delete_preset_button.grid(row=0, column=1, sticky='w', pady=10, padx=10)

# Set the geometry
root.geometry("350x405")

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
update_time_delay_button = tk.Button(root, text="Update", command=lambda: update_config('time_delay_seconds', time_delay_entry.get()))
update_time_delay_button.grid(row=1, column=2, padx=10, pady=5, sticky='w')

# Create and pack the output directory label and entry
output_directory_label = tk.Label(root, text="Gmod Directory:")
output_directory_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')
output_directory_entry = tk.Entry(root)
output_directory_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
# Populate output_directory_entry with the value from the config (if available)
output_directory_entry.insert(0, config.get('output_directory', "C:\\SteamLibrary\\steamapps\\common\\GarrysMod"))
update_output_directory_button = tk.Button(root, text="Update", command=lambda: update_config('output_directory', output_directory_entry.get()))
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
player_color_checkbox.grid(row=len(apparel_categories) + 4, column=0, padx=10, pady=5, sticky='w')

# New code for the Physgun Color checkbox
physgun_color_var = tk.IntVar()
physgun_color_checkbox = tk.Checkbutton(root, text="Physgun Color", variable=physgun_color_var)
physgun_color_checkbox.grid(row=len(apparel_categories) + 5, column=0, padx=10, pady=5, sticky='w')

# New code for the Presets checkbox
presets_var = tk.IntVar()
presets_checkbox = tk.Checkbutton(root, text="Presets", variable=presets_var)
presets_checkbox.grid(row=len(apparel_categories) + 3, column=0, padx=10, pady=5, sticky='w')

# Add the "Customize" button to the right of the "Presets" checkbox
customize_presets_button = tk.Button(root, text="Customize", command=lambda: customize_apparel("Presets"))
customize_presets_button.grid(row=len(apparel_categories) + 3, column=1, padx=10, pady=5, sticky='w')

# Checkbox for Player Color's Every Switch
player_color_every_switch_var = tk.IntVar()
player_color_every_switch_checkbox = tk.Checkbutton(root, text="Every Switch", variable=player_color_every_switch_var)
player_color_every_switch_checkbox.grid(row=len(apparel_categories) + 4, column=1, padx=10, pady=5, sticky='w')

# Checkbox for Physgun Color's Every Switch
physgun_color_every_switch_var = tk.IntVar()
physgun_color_every_switch_checkbox = tk.Checkbutton(root, text="Every Switch", variable=physgun_color_every_switch_var)
physgun_color_every_switch_checkbox.grid(row=len(apparel_categories) + 5, column=1, padx=10, pady=5, sticky='w')

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