import pyautogui
import time
from PIL import Image, ImageGrab
import os
import pygetwindow as gw


time.sleep(5)
# Function to save each image to a directory
def save_image(img, directory, file_name):
    if not os.path.exists(directory):
        os.makedirs(directory)
    img.save(os.path.join(directory, file_name))

# Directory to save individual screenshots
save_directory = '0207_screenshots'

# Get the currently active window
window = gw.getActiveWindow()
if window is None:
    raise Exception("No active window found")

# Initialize y_offset and total_height (replace with actual total height)
y_offset = 0
total_height = 1000  # Example total height of the page
window_height = window.height

# Create a full image to paste smaller screenshots
full_image = Image.new('RGB', (window.width, total_height))

# Scroll vertically and capture screenshots
while y_offset < total_height:
    window.activate()
    img = ImageGrab.grab(bbox=(window.left, window.top, window.right, window.bottom))
    
    # Paste the captured image into the full image
    full_image.paste(img, (0, y_offset))
    
    # Save each captured image to the directory
    file_name = f'screenshot_{y_offset}.png'
    save_image(img, save_directory, file_name)
    print(f'Screenshot saved: {file_name}')

    y_offset += window_height
    
    # Scroll down
    pyautogui.scroll(-window_height // 2)
    time.sleep(1)  # Wait for scrolling to complete

# Save the full stitched image
full_image.save('foreground_full_screenshot.png')
print('Full screenshot saved: full_screenshot.png')
