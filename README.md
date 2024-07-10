import os
import pygetwindow as gw
import pyautogui
import time
from PIL import Image

# Create a directory to store screenshots
image_dir = 'image_dir'
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

def capture_screenshots_while_scrolling():
    # Get active browser window
    browser_window = gw.getActiveWindow()

    if browser_window:
        # Get browser window dimensions
        browser_x, browser_y = browser_window.left, browser_window.top
        browser_width, browser_height = browser_window.width, browser_window.height
        
        print(f"Browser Window: x={browser_x}, y={browser_y}, width={browser_width}, height={browser_height}")

        # Getting total height of the webpage using a large scroll value
        total_height = 10000  # Adjust as needed to cover the entire webpage height
        
        scroll_y = 0
        screenshot_height = browser_height  # Height of each screenshot capture
        
        while scroll_y < total_height:
            # Scroll down by the height of the screen
            pyautogui.moveTo(browser_x + 100, browser_y + scroll_y + 100)  # Adjust the offset as per your screen resolution.
            pyautogui.scroll(-screenshot_height)  # Scroll down by screenshot height pixels
            
            time.sleep(0.5)  # Adjust as needed
            
            # Capture screenshot of current view
            screenshot = pyautogui.screenshot(region=(browser_x, browser_y, browser_width, browser_height))
            
            # Save screenshot to image directory with a timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_path = os.path.join(image_dir, f"screenshot_{timestamp}.png")
            screenshot.save(screenshot_path)
            
            print(f"Saved screenshot at: {screenshot_path}")
            
            # Update scroll position
            scroll_y += screenshot_height
        
        print("All screenshots saved successfully.")
    else:
        print("No active browser window found.")

# Example usage
capture_screenshots_while_scrolling()
