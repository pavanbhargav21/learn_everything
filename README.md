import time
import ctypes
from pywinauto import Desktop
from PIL import ImageGrab, Image
import pyautogui
import os


def get_foreground_window():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    return Desktop(backend="uia").window(handle=hwnd)

def get_total_scrollable_size(window):
    # Focus the window
    window.set_focus()
    
    # Get the initial visible part
    rect = window.rectangle()
    visible_height = rect.height()
    visible_width = rect.width()

    # Scroll down to the bottom and measure the total height
    pyautogui.scroll(-9999)  # Scroll down to the bottom
    time.sleep(1)
    bottom_rect = window.rectangle()
    total_height = bottom_rect.height()

    # Scroll back to the top
    pyautogui.scroll(9999)
    time.sleep(1)

    # Scroll right to the end and measure the total width
    pyautogui.hscroll(-9999)  # Scroll right to the end
    time.sleep(1)
    right_rect = window.rectangle()
    total_width = right_rect.width()

    # Scroll back to the left
    pyautogui.hscroll(9999)
    time.sleep(1)

    return total_width, total_height

def capture_entire_window(window):
    total_width, total_height = get_total_scrollable_size(window)

    # Create a blank image with the total size
    full_image = Image.new('RGB', (total_width, total_height))

    # Variables to track the current position in the full image
    y_offset = 0

    # Scroll vertically and capture screenshots
    while y_offset < total_height:
        window.set_focus()
        img = ImageGrab.grab(bbox=(window.rectangle().left, window.rectangle().top, window.rectangle().right, window.rectangle().bottom))
        full_image.paste(img, (0, y_offset))

        y_offset += window.rectangle().height()
        pyautogui.scroll(-window.rectangle().height())
        time.sleep(1)  # Wait for scrolling to complete

    # Save the final stitched image
    window_title = window.window_text().replace(" ", "_").replace(":", "").replace("\\", "").replace("/", "")
    os.makedirs("screenshots", exist_ok=True)
    full_image.save(f"screenshots/{window_title}.png")

def main():
    previous_window = None
    while True:
        current_window = get_foreground_window()
        if current_window != previous_window:
            if previous_window is not None:
                capture_entire_window(previous_window)
            previous_window = current_window
        time.sleep(1)

if __name__ == "__main__":
    main()

