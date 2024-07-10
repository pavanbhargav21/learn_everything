import threading
import time
import pygetwindow as gw
import pyautogui
from PIL import Image
import io

# Disable pyautogui fail-safe feature
pyautogui.FAILSAFE = False

def scroll_and_capture(window):
    original_pos = pyautogui.position()
    
    def perform_scroll_capture():
        # Scroll to the top of the entire window rapidly
        pyautogui.moveTo(window.left + window.width // 2, window.top + 10)
        pyautogui.mouseDown(button='left')
        pyautogui.moveTo(window.left + window.width // 2, window.top + window.height - 10, duration=0.1)
        pyautogui.mouseUp(button='left')
        
        # Capture the entire window by scrolling down
        full_screenshot = Image.new('RGB', (window.width, 10000))  # Assume max height of 10000 pixels
        y_offset = 0
        last_screenshot = None
        
        while True:
            # Capture the current view
            screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
            
            # Check if we've reached the bottom
            if last_screenshot and screenshot.tobytes() == last_screenshot.tobytes():
                break
            
            # Append the non-overlapping part of the screenshot
            if last_screenshot:
                diff = pyautogui.locate(screenshot, last_screenshot, confidence=0.9)
                if diff:
                    new_height = diff[1]
                    full_screenshot.paste(screenshot.crop((0, new_height, window.width, window.height)), 
                                          (0, y_offset + new_height))
                    y_offset += window.height - new_height
                else:
                    full_screenshot.paste(screenshot, (0, y_offset))
                    y_offset += window.height
            else:
                full_screenshot.paste(screenshot, (0, y_offset))
                y_offset += window.height
            
            last_screenshot = screenshot
            
            # Scroll down rapidly
            pyautogui.scroll(-window.height)
        
        # Crop the final image to remove any empty space
        full_screenshot = full_screenshot.crop((0, 0, window.width, y_offset))
        full_screenshot.save('full_capture.png')
        
        # Restore the original scroll position rapidly
        pyautogui.moveTo(window.left + window.width // 2, window.top + window.height - 10)
        pyautogui.mouseDown(button='left')
        pyautogui.moveTo(window.left + window.width // 2, window.top + 10, duration=0.1)
        pyautogui.mouseUp(button='left')
        
        # Restore the original mouse position
        pyautogui.moveTo(original_pos[0], original_pos[1])

    # Create a thread to perform scrolling and capturing
    thread = threading.Thread(target=perform_scroll_capture)
    thread.start()
    thread.join()  # Wait for the thread to complete

def get_active_window():
    return gw.getActiveWindow()

def on_user_action():
    window = get_active_window()
    if window:
        scroll_and_capture(window)

# Example usage: simulate user action
on_user_action()
