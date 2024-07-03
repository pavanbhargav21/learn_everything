import threading
import pygetwindow as gw
import pyautogui
import time
from PIL import ImageChops

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
        last_screenshot = None
        scroll_amount = window.height - 50  # Adjust for slight overlap

        while True:
            # Capture current view
            screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
            
            # Check if reached bottom
            if last_screenshot:
                diff = ImageChops.difference(screenshot, last_screenshot)
                if not diff.getbbox():
                    break

            # Save screenshot
            screenshot.save(f'capture_{screenshot_count:03d}.png')
            screenshot_count += 1

            last_screenshot = screenshot

            # Scroll down using Page Down key
            pyautogui.press('pagedown')
            time.sleep(0.1)  # Short wait for content load

        # Rapidly scroll back to top
        pyautogui.keyDown('ctrl')
        pyautogui.press('home')
        pyautogui.keyUp('ctrl')

        # Restore mouse position
        pyautogui.moveTo(original_pos[0], original_pos[1])

        print(f"Total screenshots: {screenshot_count}")

    thread = threading.Thread(target=perform_scroll_capture)
    thread.start()
    thread.join()

def get_active_window():
    return gw.getActiveWindow()

def on_user_action():
    window = get_active_window()
    if window:
        scroll_and_capture(window)

# Run the script
on_user_action()
