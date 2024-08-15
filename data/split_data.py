import os
import shutil
import random

# Directory paths
source_tennis_courts = "data/tennis_courts"
source_non_tennis_courts = "data/non_tennis_courts"
dataset_dir = "dataset"

# Create dataset folders if they don't exist
for category in ['test', 'train', 'validation']:
    os.makedirs(os.path.join(dataset_dir, category, 'tennis_courts'), exist_ok=True)
    os.makedirs(os.path.join(dataset_dir, category, 'non_tennis_courts'), exist_ok=True)

def split_data(source_dir, dest_dir, subfolder_name, split_ratios):
    files = os.listdir(source_dir)
    random.shuffle(files)
    
    num_files = len(files)
    test_split = int(split_ratios[0] * num_files)
    train_split = int(split_ratios[1] * num_files)
    
    splits = {
        'test': files[:test_split],
        'train': files[test_split:test_split + train_split],
        'validation': files[test_split + train_split:]
    }
    
    for category in splits:
        for file_name in splits[category]:
            src_file = os.path.join(source_dir, file_name)
            dest_file = os.path.join(dest_dir, category, subfolder_name, file_name)
            shutil.copy(src_file, dest_file)
            print(f"Copied {file_name} to {os.path.join(category, subfolder_name)}")

def count_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count

split_ratios = [0.15, 0.70, 0.15]

# Split data for tennis courts
split_data(source_tennis_courts, dataset_dir, 'tennis_courts', split_ratios)

# Split data for non-tennis courts
split_data(source_non_tennis_courts, dataset_dir, 'non_tennis_courts', split_ratios)

# Print the number of items in each subfolder
for category in ['test', 'train', 'validation']:
    tennis_courts_count = count_files(os.path.join(dataset_dir, category, 'tennis_courts'))
    non_tennis_courts_count = count_files(os.path.join(dataset_dir, category, 'non_tennis_courts'))
    print(f"{category}/tennis_courts: {tennis_courts_count} items")
    print(f"{category}/non_tennis_courts: {non_tennis_courts_count} items")
