import os
import shutil
import hashlib
import argparse
import signal
import time
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from tqdm import tqdm

SUPPORTED_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.heic',
    '.tif', '.tiff', '.nef', '.cr2', '.arw'
)

OPTIMIZABLE_FORMATS = ('.jpg', '.jpeg', '.png')

# Global flag for graceful exit
stop_processing = False

def signal_handler(sig, frame):
    global stop_processing
    print("\nInterrupt received. Stopping gracefully...")
    stop_processing = True

# Registering the signal handler
signal.signal(signal.SIGINT, signal_handler)

def parse_datetime(value):
    formats = ["%Y:%m:%d %H:%M:%S", "%Y:%m:%d %H:%M:%S.%f", "%Y:%m:%d %H:%M:%S%z"]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None

def get_exif_datetime(path):
    try:
        with Image.open(path) as image:
            exif_data = image.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']:
                        parsed_date = parse_datetime(value)
                        if parsed_date:
                            return parsed_date
    except (UnidentifiedImageError, OSError):
        pass
    return datetime.fromtimestamp(os.path.getmtime(path))

def compute_file_hash(filepath, chunk_size=8192):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except:
        return None

def organize_photos(source_dirs, dest_dir, exclude_dirs=None, move_files=False, optimize=False):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print("Destination folder created:", dest_dir)

    exclude_dirs = set(os.path.abspath(d) for d in (exclude_dirs or []))
    
    print("Reading folders...", end="", flush=True)
    total_folders = 0

    for source in source_dirs:
        for root, _, _ in os.walk(source):
            if any(os.path.abspath(root).startswith(ex) for ex in exclude_dirs):
                continue
            total_folders += 1
            print("\rReading folders... " + str(total_folders), end="", flush=True)

    print("\nFound", total_folders, "folders to process (excluding", len(exclude_dirs), "folders).\n")

    processed_folders = 0
    total_files = 0
    total_new_files = 0
    total_skipped_files = 0
    total_renamed_files = 0
    total_size = 0
    start_time = time.time()

    for source_folder in source_dirs:
        if not os.path.isdir(source_folder):
            print("Source folder not found:", source_folder)
            continue

        for root, _, files in os.walk(source_folder):
            if stop_processing:
                print("Stopped processing.")
                return

            if any(os.path.abspath(root).startswith(ex) for ex in exclude_dirs):
                continue

            image_files = [f for f in files if f.lower().endswith(SUPPORTED_EXTENSIONS)]
            if not image_files:
                continue

            processed_folders += 1
            print("Processing folder", processed_folders, "/", total_folders, ":", root)

            for file in tqdm(image_files, desc="Processing " + os.path.basename(root), unit="file", leave=False):
                if stop_processing:
                    print("Stopping... Please wait.")
                    return

                full_path = os.path.join(root, file)
                total_files += 1
                total_size += os.path.getsize(full_path)

                try:
                    date_taken = get_exif_datetime(full_path)
                except ValueError:
                    print("Skipping file with invalid date format:", file)
                    continue

                subfolder = date_taken.strftime("%Y/%m")
                dest_path = os.path.join(dest_dir, subfolder)
                os.makedirs(dest_path, exist_ok=True)

                dest_file = os.path.join(dest_path, file)
                
                if os.path.exists(dest_file):
                    src_hash = compute_file_hash(full_path)
                    dest_hash = compute_file_hash(dest_file)

                    if src_hash == dest_hash:
                        total_skipped_files += 1
                        continue
                    else:
                        base, ext = os.path.splitext(file)
                        dest_file = os.path.join(dest_path, base + "_copy" + ext)
                        total_renamed_files += 1

                try:
                    if move_files:
                        shutil.move(full_path, dest_file)
                    else:
                        shutil.copy2(full_path, dest_file)

                    total_new_files += 1

                    if optimize and dest_file.lower().endswith(OPTIMIZABLE_FORMATS):
                        optimize_image(dest_file)
                except Exception as e:
                    print("Error processing", file, ":", e)

    end_time = time.time()
    duration = end_time - start_time

    print("\nFinal Report:")
    print("Total folders processed:", processed_folders)
    print("Total files processed:", total_files)
    print("New files:", total_new_files, ", Skipped:", total_skipped_files, ", Renamed:", total_renamed_files)
    print("Total size processed:", "{:.2f} MB".format(total_size / (1024 * 1024)))
    print("Total time taken:", "{:.2f} seconds".format(duration))

def optimize_image(image_path):
    try:
        with Image.open(image_path) as img:
            ext = os.path.splitext(image_path)[1].lower()
            temp_path = image_path + ".opt"
            if ext in ('.jpg', '.jpeg'):
                img.save(temp_path, 'JPEG', quality=95, optimize=True)
            elif ext == '.png':
                img.save(temp_path, 'PNG', optimize=True)
            if os.path.getsize(temp_path) < os.path.getsize(image_path):
                os.replace(temp_path, image_path)
            else:
                os.remove(temp_path)
    except (UnidentifiedImageError, OSError):
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Organize images by date taken (EXIF or file timestamp).")
    parser.add_argument('--source', '-s', nargs='+', required=True, help='Source folder(s)')
    parser.add_argument('--dest', '-d', required=True, help='Destination folder')
    parser.add_argument('--exclude', '-e', nargs='+', help='Folder(s) to exclude from processing')
    parser.add_argument('--move', '-m', action='store_true', help='Move files instead of copying them')
    parser.add_argument('--optimize', '-o', action='store_true', help='Optimize JPEG/PNG images after organizing')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    organize_photos(args.source, args.dest, exclude_dirs=args.exclude, move_files=args.move, optimize=args.optimize)
