import os
import random

# Define the path to your directory
directory = 'data/non_tennis_court_images'

# List all files in the directory
files = os.listdir(directory)

# Shuffle the files to mix urban and suburban images
random.shuffle(files)

# Define the new base name and file extension
new_base_name = "non_court"
file_extension = ".png"  # Change this if your files have a different extension

# Iterate through the files and rename them
for index, file in enumerate(files):
    old_path = os.path.join(directory, file)
    new_file_name = f"{new_base_name}_{index+1:04d}{file_extension}"  # 04d for zero-padding
    new_path = os.path.join(directory, new_file_name)
    os.rename(old_path, new_path)

print("Files have been renamed and reordered.")
