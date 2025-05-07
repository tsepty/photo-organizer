# Photo Organizer & Optimizer

This Python script organizes your image files from one or more source folders into a structured destination folder (Year/Month) based on the date the photo was taken (via EXIF metadata or file modification time). It also offers optional optimization for JPEG and PNG files, supports duplicate detection using hash checks, and provides a detailed final report.

---

## Features

- Organize photos by Year/Month folders.
- Supports multiple source folders.
- Detects "date taken" from EXIF metadata or file timestamp.
- Avoids duplicate files using hash comparison (SHA-256).
- Automatically renames files with different hash (e.g., `image_copy.jpg`).
- Optional lossless optimization for JPEG/PNG.
- Choose to either copy (default) or move files.
- Real-time progress bar with `tqdm`.
- Displays total folders and progress.
- Graceful Ctrl+C (SIGINT) handling for clean stop.
- Exclude specific folders with `--exclude`.
- Detailed Final Report:
  - Total folders processed.
  - Total files processed.
  - New files, Skipped files, Renamed files (hash difference).
  - Total size processed (MB).
  - Total time taken.

---

## Requirements

- Python 3.7+
- Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python photo-organizer.py --source <source_folder1> <source_folder2> ... --dest <destination_folder> [options]
```

### Examples

**Copy files from multiple folders:**
```bash
python photo-organizer.py --source "Z:\Pictures" "Z:\Old" --dest "Z:\Catalog"
```

**Move files instead of copying:**
```bash
python photo-organizer.py --source "Z:\PhoneBackup" --dest "Z:\Catalog" --move
```

**Optimize JPEG and PNG images:**
```bash
python photo-organizer.py --source "Z:\DCIM" --dest "Z:\Catalog" --optimize
```

**Exclude specific folders:**
```bash
python photo-organizer.py --source "Z:\Pictures" --dest "Z:\Catalog" --exclude "Z:\Pictures\SkipThis"
```

---

## Options
- `--source` or `-s` - Source folder(s).
- `--dest` or `-d` - Destination folder (will be created if missing).
- `--exclude` or `-e` - Folder(s) to exclude from processing.
- `--move` or `-m` - Move files instead of copying.
- `--optimize` or `-o` - Optimize JPEG/PNG images.
- Graceful Stop: Use `Ctrl+C` to stop the process cleanly at any time.

---

## Final Report Details
- Total folders processed.
- Total files processed.
- New files (copied/moved), Skipped (identical hash), Renamed (hash difference).
- Total size processed (MB).
- Total time taken.
