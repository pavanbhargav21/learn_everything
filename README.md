import pygetwindow as gw
import pyautogui
import pytesseract
import cv2
import re
import time
from PIL import Image

DELAY=0.1

# Configure pytesseract path if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path to your Tesseract installation

def get_active_window():
    active_window = gw.getActiveWindow()
    if active_window:
        return active_window.title, active_window
    return None, None

def capture_screenshot(window):
    # Get the dimensions of the active window
    global DELAY
    left, top, right, bottom = window.left, window.top, window.right, window.bottom
    screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
    DELAY+=1
    stitched_image_path = f"page_screenshot_{DELAY}.png"
    screenshot.save(stitched_image_path)
    return stitched_image_path

def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Use OCR to extract text
    text = pytesseract.image_to_string(gray)
    return text

def extract_urls(text):
    url_pattern = re.compile(r'(https?://\S+)')
    urls = url_pattern.findall(text)
    return urls

def monitor_active_window():
    last_active_window = None
    while True:
        window_title, active_window = get_active_window()
        if window_title and window_title != last_active_window:
            print(f"Active application changed to: {window_title}")
            screenshot_path = capture_screenshot(active_window)
            text = extract_text_from_image(screenshot_path)
            urls = extract_urls(text)
            if urls:
                print(f"URLs found: {urls}")
            else:
                print("No URLs found")
            last_active_window = window_title
        time.sleep(2)

if __name__ == "__main__":
    monitor_active_window()
