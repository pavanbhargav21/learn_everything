import time
import pyautogui
from PIL import Image

# Function to capture and stitch screenshots
def capture_full_page_screenshot():
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    
    # Assume browser window is at some fixed position and size
    browser_x = 0
    browser_y = 0
    browser_width = screen_width  # Adjust based on your browser window size
    browser_height = screen_height  # Adjust based on your browser window size
    
    # Set initial scroll position and screenshot size
    scroll_x, scroll_y = browser_x, browser_y
    screenshot_width, screenshot_height = browser_width, 1000  # Adjust height based on your screen resolution
    
    # Initialize the stitched image
    stitched_image = Image.new('RGB', (screenshot_width, browser_height))

    while scroll_y < browser_height:
        # Scroll down by the height of the screen
        pyautogui.moveTo(scroll_x + 100, scroll_y + 100)  # Adjust the offset as per your screen resolution.
        pyautogui.scroll(-1000)  # Scroll down by 1000 pixels (adjust as needed)
        time.sleep(0.5)  # Adjust as needed
        
        # Capture screenshot of current view
        screenshot = pyautogui.screenshot(region=(scroll_x, scroll_y, screenshot_width, screenshot_height))
        stitched_image.paste(screenshot, (0, scroll_y))
        
        # Update scroll position
        scroll_y += screenshot_height
    
    # Save the final stitched image
    stitched_image.save('auto_full_page_screenshot.png')

# Example usage
time.sleep(2)
capture_full_page_screenshot()
