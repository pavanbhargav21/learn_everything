import pygetwindow as gw
import time
import pyautogui
from PIL import ImageGrab, Image
import io
from selenium import webdriver

def get_active_window():
    active_window = gw.getActiveWindow()
    if active_window:
        return active_window.title
    return None

def capture_screenshot_window(window_title):
    # Get the dimensions of the active window
    window = gw.getWindowsWithTitle(window_title)[0]
    left, top, right, bottom = window.left, window.top, window.right, window.bottom
    screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
    
    # Save the screenshot with a timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    print(window_title)
    window_title_name = window_title.split("|")[0].split("/")[0]
    screenshot.save(f"screenshot_{window_title_name}_{timestamp}.png")
    print(f"Screenshot saved for {window_title} at {timestamp}")

def monitor_active_window():
    last_active_window = None
    while True:
        active_window = get_active_window()
        if active_window and active_window != last_active_window:
            print(f"Active application changed to: {active_window}")
            capture_screenshot_window(active_window)
            last_active_window = active_window
        time.sleep(2)

def capture_full_page_screenshot(driver):
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    stitched_image = Image.new('RGB', (driver.execute_script("return document.body.scrollWidth"), total_height))

    # Scroll and capture screenshots
    offset = 0

    while offset < total_height:
        driver.execute_script(f"window.scrollTo(0, {offset});")
        delay = 0.5
        time.sleep(delay)  # Allow some time for scrolling
        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(io.BytesIO(screenshot))
        
        stitched_image.paste(screenshot, (0, offset))
        offset += viewport_height

    # Save the final stitched image
    stitched_image_path = f"page_screenshot_{delay}.png"
    stitched_image.save(stitched_image_path)

# The functions below are defined but never integrated into the flow.
# Implement these if requird
def track_user_interaction(url):
    driver = webdriver.Chrome()
    driver.get(url)
    
    while True:
        # Check for login status
        login_status = check_login_status(driver)
        if login_status:
            print("User logged in, starting tracking.")
            start_tracking(driver)
        time.sleep(1)

def start_tracking(driver):
    while True:
        # Check if submit button is clicked
        if submit_button_clicked(driver):
            capture_full_page_screenshot(driver)
            break
        time.sleep(1)

def check_login_status(driver):
    return True

def submit_button_clicked(driver):
    return True

# Start monitoring the active window
monitor_active_window()
