import threading
import time
import pygetwindow as gw
import pyautogui

def capture_entire_window(window, interval=15, duration=60):
    def scroll_and_capture():
        original_pos = pyautogui.position()

        # Get the initial scroll position
        initial_scroll_pos = None
        # Capture screenshots in intervals
        for _ in range(4):  # Capture 4 times
            time.sleep(interval)
            # Scroll to top
            pyautogui.click(window.left + 10, window.top + 10)  # Bring window to foreground
            if initial_scroll_pos is None:
                initial_scroll_pos = pyautogui.position()  # Save initial position once
            
            pyautogui.scroll(100000)  # Scroll to top (assuming large enough value)
            time.sleep(1)  # Wait for scroll to complete
            
            # Capture the entire window by scrolling down
            for i in range(10):  # Adjust range for more/less scrolling
                screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
                screenshot.save(f'capture_{i}.png')
                pyautogui.scroll(-window.height)  # Scroll down by window height
                time.sleep(0.2)  # Short delay between scrolls

            # Restore original scroll position
            pyautogui.scroll(100000)  # Scroll to top first
            pyautogui.scroll(-100000)  # Scroll to bottom (assuming large enough value)

            if initial_scroll_pos:
                pyautogui.moveTo(initial_scroll_pos[0], initial_scroll_pos[1])

            # Restore mouse position
            pyautogui.moveTo(original_pos[0], original_pos[1])

    # Start the thread
    thread = threading.Thread(target=scroll_and_capture)
    thread.start()

def get_active_window():
    active_window = gw.getActiveWindow()
    return active_window

def on_user_action():
    window = get_active_window()
    if window:
        capture_entire_window(window)

# Example usage: simulate user action
on_user_action()
