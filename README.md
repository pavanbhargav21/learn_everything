import threading
import pygetwindow as gw
import pyautogui
import time
import numpy as np
from PIL import Image

# Disable pyautogui fail-safe feature
pyautogui.FAILSAFE = False
time.sleep(5)
def scroll_and_capture(window):
    original_pos = pyautogui.position()
    
    def perform_scroll_capture():
        # Ensure window is active
        window.activate()
        time.sleep(0.1)

        # Rapidly scroll to the top
        pyautogui.moveTo(window.left + window.width // 2, window.top + 10)
        pyautogui.click()
        pyautogui.keyDown('ctrl')
        pyautogui.press('home')
        pyautogui.keyUp('ctrl')
        time.sleep(0.2)

        screenshot_count = 0
        scroll_count = 0
        last_screenshot = None

        while True:
            # Capture current view
            screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
            
            # Check if reached bottom
            if last_screenshot:
                if images_equal(screenshot, last_screenshot):
                    break

            # Save screenshot
            screenshot.save(f'capture_{screenshot_count:03d}.png')
            screenshot_count += 1

            last_screenshot = screenshot

            # Scroll down
            pyautogui.press('pagedown')
            scroll_count += 1
            time.sleep(0.1)  # Short wait for content load

        # Scroll back to the original position
        for _ in range(scroll_count):
            pyautogui.press('pageup')
            time.sleep(0.05)

        # Restore mouse position
        pyautogui.moveTo(original_pos[0], original_pos[1])

        print(f"Total screenshots: {screenshot_count}")

    thread = threading.Thread(target=perform_scroll_capture)
    thread.start()
    thread.join()

def images_equal(img1, img2):
    # Convert PIL Images to numpy arrays
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    
    # Compare the arrays
    return np.array_equal(arr1, arr2)

def get_active_window():
    return gw.getActiveWindow()

def on_user_action():
    window = get_active_window()
    if window:
        scroll_and_capture(window)

# Run the script
on_user_action()
