import os
import pathlib
import shutil

from bft.html.builder import build_site

def copy_with_progress(src, dst, copy_function=shutil.copy2):
    for root, dirs, files in os.walk(src):
        relative_path = os.path.relpath(root, src)
        destination_path = os.path.join(dst, relative_path)

        os.makedirs(destination_path, exist_ok=True)

        for file in files:
            source_file = os.path.join(root, file)
            destination_file = os.path.join(destination_path, file)
            copy_function(source_file, destination_file)
            print(f"Copying: {source_file} -> {destination_file}")

root = pathlib.Path(__file__).parent.resolve()
index = root / "index.yaml"
dest = root / "dist"

# Remove the destination directory if it exists
if dest.exists():
    shutil.rmtree(dest)

# Create the destination directory
os.mkdir(dest)

build_site(str(index), str(dest))

static_content_dir = root / "static_site"

# Use the custom copy_with_progress function
copy_with_progress(static_content_dir, dest)

print("Copying static files completed.")
