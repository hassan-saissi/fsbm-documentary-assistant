from pathlib import Path
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("root", help="Path to data/raw")
parser.add_argument(
    "--apply",
    action="store_true",
    help="Actually move files and remove empty folders"
)
args = parser.parse_args()

root = Path(args.root).resolve()
categories = {"cours", "td", "tp"}

if not root.is_dir():
    raise SystemExit(f"Directory not found: {root}")

# Find category folders, processing the deepest ones first
folders = sorted(
    (
        p for p in root.rglob("*")
        if p.is_dir() and p.name.lower() in categories
    ),
    key=lambda p: len(p.parts),
    reverse=True,
)

for folder in folders:
    parent = folder.parent

    # Collect files recursively
    files = sorted(p for p in folder.rglob("*") if p.is_file())

    for src in files:
        # Keep filenames unique; never overwrite existing files
        dest = parent / src.name
        counter = 2

        while dest.exists():
            dest = parent / f"{src.stem}_{counter}{src.suffix}"
            counter += 1

        print(f"{'MOVE' if args.apply else 'WOULD MOVE'}: "
              f"{src} -> {dest}")

        if args.apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))

    if args.apply:
        # Remove the category folder only if it is now empty
        for directory in sorted(
            (p for p in folder.rglob("*") if p.is_dir()),
            key=lambda p: len(p.parts),
            reverse=True,
        ):
            if not any(directory.iterdir()):
                directory.rmdir()

        if not any(folder.iterdir()):
            folder.rmdir()

print("\nFinished." if args.apply else
      "\nPreview only. Run again with --apply to make changes.")

# to applay this code use this script on Git Bash or Ubuntu 
# python merge_resources.py data/raw --> to see all files that will moving 
# python merge_resources.py data/raw --apply --> to execute the code 