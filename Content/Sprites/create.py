import os
from PIL import Image
from PIL import ImageSequence
import numpy as np
import imageio
import getpass
import shutil
import sys

os.environ['IMAGEIO_MAX_IMAGE_PIXELS'] = '512000000'  # Increase to 512MB

username = getpass.getuser()
input_folder = rf"C:\Users\{username}\Documents\GitHub\HideAndSneak\Content\Sprites"
head_folder = os.path.join(input_folder, "head_poses")
run_folder = os.path.join(input_folder, "run_animation")
output_folder = input_folder
body_image = os.path.join(output_folder, "body.png")


anim_gifs_folder = os.path.join(output_folder, "anim_gifs")

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
        "skin1": "#b97a56",
        "skin2": "#da7338"
    },
    "darkest": {
        "skin1": "#da7338",
        "skin2": "#b24900"
    }
}

player_numbers = ["one", "two", "three", "four", "five", "six"]

def create_players():
    for player in player_numbers:
        create_animations(player)

def create_animations(player):
    for color in skin_colors:
        create_animation(color, player)

def create_animation(color, player):
    run_frames = [os.path.join(run_folder, f) for f in os.listdir(run_folder) if f.endswith('.png')]
    run_frames.sort()  # Ensure frames are in order

    # Define folder structure
    subfolders = ["left", "right"]

    player_folder = os.path.join(anim_gifs_folder, f"player_{player}")

    folder_path = os.path.join(player_folder, color)
    os.makedirs(folder_path, exist_ok=True)

    for subfolder in subfolders:
        subfolder_path = os.path.join(folder_path, subfolder)
        os.makedirs(subfolder_path, exist_ok=True)

        print(f"Processing folder: {color}/{subfolder}")

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

            if subfolder == "right":
                # Flip run image horizontally for "right" folder
                body_image_loaded = body_image_loaded.transpose(Image.FLIP_LEFT_RIGHT)

            gif_frames = []  # Clear gif_frames for each head pose

            for i, run_frame in enumerate(run_frames):
                head_pose_name = head_pose_file.replace(".png", "")
                print(f"\nCreating frame {i+1}/{len(run_frames)} for player {player}'s run animation of {color} for {head_pose_name}")
                run_image = Image.open(run_frame).copy()  # Make a copy of run_image for each frame
                body_image_loaded = Image.open(body_image)
                
                if subfolder == "right":
                    # Flip run image horizontally for "right" folder
                    run_image = run_image.transpose(Image.FLIP_LEFT_RIGHT)

                print(f"    Adding body image")
                combined_frame = body_image_loaded.copy()
                
                print(f"    Adding run image at position (0, 20)")
                combined_frame.paste(run_image, (0, -20, run_image.width, run_image.height - 20))
                
                transpose = 0
                if (i % 3 != 0): transpose = 20 # every third frame

                print(f"    Adding head image at position (0, {transpose})")
                if subfolder == "left":
                    combined_frame.paste(head_image, (0, transpose), head_image)
                else:
                    # Adjust position for flipped head image
                    combined_frame.paste(head_image, (combined_frame.width - head_image.width, transpose), head_image)
                
                combined_frame = replace_color(combined_frame, skin_colors.get("tan").get("skin1"), skin_colors.get(color).get("skin1"))
                combined_frame = replace_color(combined_frame, skin_colors.get("tan").get("skin2"), skin_colors.get(color).get("skin2"))
                gif_frames.append(combined_frame)

            output_file = os.path.join(subfolder_path, f"{color}_{subfolder}_{head_pose_name}_run_anim.gif").lower()
            save_frames_as_gif(gif_frames, output_file)
            print(f"\nGenerated GIF: {output_file}")
            # create_individual_png_frames(gif_frames, output_folder)

def save_frames_as_gif(frames, output_path):
    # Set disposal to 2 to clear the previous frame
    # Set loop to 0 to loop forever
    print("\nSaving GIF, this may take a few seconds!")
    kwargs = {'duration': 0.1, 'disposal': 2, 'loop': 0}
    imageio.mimsave(output_path, frames, **kwargs)

def create_individual_png_frames(frames, output_folder):
    for i, frame in enumerate(frames):
        output_file = os.path.join(output_folder, f"frame_{i}.png")
        frame.save(output_file, format="PNG")

def copy_and_replace():
    for folder_name, colors in skin_colors.items():
        print(f"Processing folder: {folder_name}")
        source_folder = os.path.join(player1_folder, "tan")
        target_folder = os.path.join(player1_folder, folder_name)

        os.makedirs(target_folder, exist_ok=True)

        for subfolder in os.listdir(source_folder):
            subfolder_path = os.path.join(source_folder, subfolder)
            if not os.path.isdir(subfolder_path):
                continue

            for filename in os.listdir(subfolder_path):
                source_file = os.path.join(subfolder_path, filename)
                target_filename = filename.replace("tan", folder_name, 1)
                target_file = os.path.join(target_folder, target_filename)  # Remove subfolder from target path
                print(f"Processing file: {target_filename}")
                

                if filename.endswith('.gif'):
                    print("Processing GIF file")
                    new_gif = []
                    with imageio.get_reader(source_file) as reader:
                        for i, frame in enumerate(reader):
                            print(f"Processing frame {i+1}")
                            frame = Image.fromarray(frame).convert("RGBA")  # Convert frame to RGBA
                            frame = replace_color(frame, "#fec087", colors["skin1"])
                            frame = replace_color(frame, "#e15351", colors["skin2"])
                            new_gif.append(frame)
                    print("Saving GIF file")
                    save_frames_as_gif(new_gif, target_file)
                    # new_gif[0].save(target_file, save_all=True, append_images=new_gif[1:], loop=0, disposal=2, transparency=0)


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

def create_player_folders(head_folder, output_folder):
    # Define player colors
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

    # Iterate over each player
    for player, colors in player_colors.items():
        player_folder = os.path.join(output_folder, player)
        player_one_folder = os.path.join(output_folder, "player_one")

        # Copy player_one folder to new player folder
        shutil.copytree(player_one_folder, player_folder)

        # Replace colors for each player
        copy_and_replace(head_folder, player_folder, colors)

# START
if (len(sys.argv) > 1 and sys.argv[1] == "copy"):
    copy_and_replace()
else:
    create_players()


# Authored by Copilot AI