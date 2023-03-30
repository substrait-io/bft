import os
import pathlib
import shutil

from bft.html.builder import build_site

root = pathlib.Path(__file__).parent.resolve()
index = root / "index.yaml"
dest = root / "dist"

shutil.rmtree(dest, ignore_errors=True)
os.mkdir(dest)

build_site(str(index), str(dest))

static_content_dir = root / "static_site"
for path in os.listdir(static_content_dir):
    print(f"Copying static file: {path}")
    shutil.copy2(static_content_dir / path, dest)
