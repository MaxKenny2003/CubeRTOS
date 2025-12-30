from picamera2 import Picamera2
import time
from pathlib import Path
import shutil
import logging_events_helper

# -----------------------------------------------------------
# CONFIG (relative paths)
# -----------------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()   # folder where script is located
IMAGE_DIR = BASE_DIR / "Images"
ARCHIVE_ROOT = BASE_DIR / "ImagesNotSent"
MAX_IMAGES = 10
# -----------------------------------------------------------

def ensure_archive_folder():
    """Create the next archive folder (Images0, Images1, Images2...)."""
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)

    existing = [p for p in ARCHIVE_ROOT.glob("Images*") if p.is_dir()]
    nums = []

    for p in existing:
        try:
            nums.append(int(p.name.replace("Images", "")))
        except ValueError:
            pass

    next_num = max(nums) + 1 if nums else 0
    new_folder = ARCHIVE_ROOT / f"Images{next_num}"
    new_folder.mkdir()
    return new_folder


def rotate_images_if_needed():
    """Move all images to a new archive folder if we exceed MAX_IMAGES."""
    jpg_files = list(IMAGE_DIR.glob("*.jpg"))

    if len(jpg_files) <= MAX_IMAGES:
        return

    archive_folder = ensure_archive_folder()
    print(f"📦 Moving {len(jpg_files)} images → {archive_folder}")

    for file in jpg_files:
        shutil.move(str(file), archive_folder)


def take_photo():
    """Take a photo and save it as ImageN.jpg."""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    jpg_files = list(IMAGE_DIR.glob("*.jpg"))
    num = len(jpg_files)

    filename = IMAGE_DIR / f"Image{num}.jpg"
    logging_events_helper.picture_log(f"Image{num}.jpg")

    # Initialize Picamera2
    camera = Picamera2()
    camera.configure(camera.create_preview_configuration(
        main={"format": "XRGB8888", "size": (640, 480)}
    ))
    camera.start()
    time.sleep(2)  # let camera adjust

    # CORRECT method in Picamera2
    camera.capture_file(str(filename))  # <- changed from capture()
    camera.stop()
    print(f"📸 Saved: {filename}")



# -----------------------------------------------------------
# MAIN EXECUTION
# -----------------------------------------------------------
if __name__ == "__main__":
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    rotate_images_if_needed()
    take_photo()
