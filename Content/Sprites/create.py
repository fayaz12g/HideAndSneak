import os
import time
from PIL import Image
from PIL import ImageSequence
import numpy as np
import imageio
import getpass
import shutil
import sys
from threading import Thread
import concurrent.futures
import time

os.environ['IMAGEIO_MAX_IMAGE_PIXELS'] = '512000000'  # Increase to 512MB

username = getpass.getuser()
input_folder = rf"C:\Users\{username}\Documents\GitHub\HideAndSneak\Content\Sprites"
head_folder = os.path.join(input_folder, "head_poses")
run_folder = os.path.join(input_folder, "run_animation")
output_folder = input_folder
sneaker_body_image = os.path.join(output_folder, "sneaker_body.png")
seeker_body_image = os.path.join(output_folder, "seeker_body.png")

base_colors = {
    "skin1": "#fec087",
    "skin2": "#e15351",
    "clothdarkest": "#111111",
    "clothdark":  "#b97a56",
    "clothlight": "#ffaec8",
}

# Define skin color replacements
skin_colors = {
    "tan": {
        "skin1": "#fec087",
        "skin2": "#e15351"
    },
    "light": {
        "skin1": "#fdeca6",
        "skin2": "#ffca18"
    },
    "dark": {
        "skin1": "#b98161",
        "skin2": "#da7338"
    },
    "darkest": {
        "skin1": "#64422e",
        "skin2": "#b24900"
    }
}

player_colors = {
    "player_one": {
        "clothdarkest": "#111111",
        "clothdark":  "#252a3d",
        "clothlight": "#637e93",
    },
    "player_two": {
        "clothdarkest": "#88001b",
        "clothdark": "#ec1c24",
        "clothlight": "#f05c62"
    },
    "player_three": {
        "clothdarkest": "#0b852d",
        "clothdark": "#0ed145",
        "clothlight": "#c4ff0e"
    },
    "player_four": {
        "clothdarkest": "#3f48cc",
        "clothdark": "#00a8f3",
        "clothlight": "#8cfffb"
    },
    "player_five": {
        "clothdarkest": "#f68821",
        "clothdark": "#ffca18",
        "clothlight": "#fff200"
    },
    "player_six": {
        "clothdarkest": "#4a0f4b",
        "clothdark": "#b83dba",
        "clothlight": "#ffaec8"
    }
}

player_types = ["sneaker"]
player_directions = ["left", "right"]
debug_options = ["y", "n"]

# Initialize selected vars to be updated upon user input
selected_types = None
selected_nums = None
selected_colors = None
selected_dirs = None
selected_debug = "y"

def create_players(type, selected_debug):
    timestart = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=96) as executor:
        futures = []
        for player_num in selected_nums:
            future = executor.submit(create_animations, player_num, type, selected_debug)
            futures.append(future)

        # Wait for all threads to finish
        concurrent.futures.wait(futures)

    timeend = time.time()
    timetotal = timeend - timestart
    print(f"Total execution time: {timetotal:.2f} seconds")

def create_animations(player, type, selected_debug):
    for color in selected_colors: # for each skin color
        create_animation(color, player, type, selected_debug)

def create_animation(color, player, type, selected_debug):
    run_frames = [os.path.join(run_folder, f) for f in os.listdir(run_folder) if f.endswith('.png')]
    run_frames.sort()  # Ensure frames are in order

    # Define folder structure
    subfolders = selected_dirs
    player_folder = os.path.join(output_folder, f"{type}_anim_gifs", player)
    folder_path = os.path.join(player_folder, color)
    os.makedirs(folder_path, exist_ok=True)

    for subfolder in subfolders:
        subfolder_path = os.path.join(folder_path, subfolder)
        os.makedirs(subfolder_path, exist_ok=True)

        if selected_debug == "y":
            print(f"Processing folder: {color}/{subfolder}:\n")

        for head_pose_file in os.listdir(head_folder):
            if not head_pose_file.endswith('.png'):
                continue
            head_pose = os.path.join(head_folder, head_pose_file)
            head_pose_name = os.path.splitext(head_pose_file)[0]
            head_image = Image.open(head_pose)
            head_image = head_image.convert("RGBA")  # Ensure image mode is RGBA for transparency

            if subfolder == "right":
                # Flip head image horizontally for "right" folder
                head_image = head_image.transpose(Image.FLIP_LEFT_RIGHT)
            
            print(f"Generating animation for {color} {player}'s {subfolder} {head_pose_name}")

            gif_frames = []  # Initialize gif_frames for each head pose
            frame_workers = [] # Initialize array to store worker threads

            for i, run_frame in enumerate(run_frames):
                head_pose_name = head_pose_file.replace(".png", "")
                
                frame_thread = Thread(target = create_anim_frame, args = (player, color, type, subfolder, run_frame, i, len(run_frames), head_image, head_pose_name, gif_frames, selected_debug))
                frame_workers.append(frame_thread)
                frame_thread.start()
            
            for thread in frame_workers: # wait for all threads to complete
                thread.join()

            if selected_debug == "n":
                print("\n")

            output_file = os.path.join(subfolder_path, f"{color}_{subfolder}_{head_pose_name}_run_anim.gif").lower()
            gif_thread = Thread(target = save_frames_as_gif, args = (gif_frames, output_file))
            gif_thread.start()

def create_anim_frame(player, color, type, subfolder, run_frame, frame_num, num_frames, head_image, head_pose_name, gif_frames, selected_debug):
    output_string = f"\nCreated {subfolder} frame {frame_num+1}/{num_frames} of {color} {player}'s run animation for {head_pose_name}\n"
    run_image = Image.open(run_frame).copy()  # Make a copy of run_image for each frame
    body_image_loaded = Image.open(getattr(sys.modules[__name__], f"{type}_body_image"))

    if subfolder == "right":
        # Flip run image horizontally for "right" folder
        body_image_loaded = body_image_loaded.transpose(Image.FLIP_LEFT_RIGHT)
    
    if subfolder == "right":
        # Flip run image horizontally for "right" folder
        run_image = run_image.transpose(Image.FLIP_LEFT_RIGHT)

    output_string += f"    Added body image\n"
    combined_frame = body_image_loaded.copy()
    
    output_string += f"    Added run image at position (0, 20)\n"
    combined_frame.paste(run_image, (0, -20, run_image.width, run_image.height - 20))
    
    transpose = 0
    if (frame_num % 3 != 0): transpose = 20 # every third frame

    output_string += f"    Added head image at position (0, {transpose})\n"
    if subfolder == "left":
        combined_frame.paste(head_image, (0, transpose), head_image)
    else:
        # Adjust position for flipped head image
        combined_frame.paste(head_image, (combined_frame.width - head_image.width, transpose), head_image)

    for skin in skin_colors.get(color):
        output_string += f"\n    Replaced {base_colors.get(skin)} with {skin_colors.get(color).get(skin)}"
        combined_frame = replace_color(combined_frame, base_colors.get(skin), skin_colors.get(color).get(skin))

    for cloth in player_colors.get(player):
        output_string += f"\n    Replaced {base_colors.get(cloth)} with {player_colors.get(player).get(cloth)}"
        combined_frame = replace_color(combined_frame, base_colors.get(cloth), player_colors.get(player).get(cloth))

    if selected_debug == "y":
        print(output_string)
    gif_frames.append(combined_frame)

def save_frames_as_gif(frames, output_path):
    # Set disposal to 2 to clear the previous frame
    # Set loop to 0 to loop forever
    if selected_debug == "y":
        print(f"\nSaving GIF: {output_path}\n")
    kwargs = {'duration': 0.1, 'disposal': 2, 'loop': 0}
    imageio.mimsave(output_path, frames, **kwargs)

def create_individual_png_frames(frames, output_folder):
    for i, frame in enumerate(frames):
        output_file = os.path.join(output_folder, f"frame_{i}.png")
        frame.save(output_file, format="PNG")

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def replace_color(image, old_color, new_color):
    old_color = hex_to_rgb(old_color)
    new_color = hex_to_rgb(new_color)
    data = np.array(image)
    
    # Create masks for pixels that match the old color
    mask = np.all(data[:, :, :3] == old_color, axis=-1)
    
    # Update pixels that match the old color with the new color
    data[..., :3][mask] = new_color
    
    return Image.fromarray(data, mode=image.mode)  # Ensure the returned image has the same mode

def input_parameter(param, example, selected_list, all):
    while(selected_list == None):
        # Input user's list of param elements for current param
        input_list = input(f"Player {param.capitalize()}s (e.g. {example.lower()}): ").strip().split(" ")

        # default to all if nothing was inputted
        if (input_list[0] == "" and len(input_list) == 1):
            return all

        # Iterate through each param element to ensure it is valid for that param
        found_error = False
        for input_element in input_list:
            if input_element not in all:
                print(f"  Error: {input_element} is not a valid player {param.lower()}. Try again.")
                found_error = True
                break
        if (not found_error): return input_list

# START
print("-----------------------------------------------------------------------------------")
print("|                        HIDE AND SNEAK: ANIMATION CREATOR                        |")
print("|                                                                                 |")
print("| For each of the following, enter a space-separated list of options to generate. |")
print("|                    e.g. 'player_one player_three player_six'                    |")
print("|                      (Or leave blank to generate all)                           |")
print("|---------------------------------------------------------------------------------|")
print()

selected_types = input_parameter("type", "sneaker", selected_types, player_types)
selected_nums = input_parameter("number", "player_one", selected_nums, list(player_colors.keys()))
selected_colors = input_parameter("color", "tan", selected_colors, list(skin_colors.keys()))
selected_dirs = input_parameter("direction", "left", selected_dirs, player_directions)
selected_debug = input("Show Debug: (y/n): ")
if selected_debug == "\n":
    selected_debug == "n"

for type in player_types:
    create_players(type, selected_debug)