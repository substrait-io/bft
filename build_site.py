import shutil
from pathlib import Path

from bft.html.builder import build_site


def copy_with_progress(src, dst, copy_function=shutil.copy2):
    for source_path in Path(src).rglob('*'):
        relative_path = source_path.relative_to(src)
        destination_path = dst / relative_path

        if source_path.is_file():
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            copy_function(source_path, destination_path)
            print(f"Copying: {source_path} -> {destination_path}")

root = Path(__file__).parent.resolve()
index = root / "index.yaml"
dest = root / "dist"

# Remove the destination directory if it exists
if dest.exists():
    shutil.rmtree(dest)

# Create the destination directory
dest.mkdir()

build_site(index, dest)

static_content_dir = root / "static_site"

# Use the custom copy_with_progress function
copy_with_progress(static_content_dir, dest)

print("Copying static files completed.")
