from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
from PIL import Image
import io

USERNAME="pavanbhargav21"
PASSWORD="Chintunani@2121"


# Set up Chrome options
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run in headless mode for no GUI
#chrome_options.add_argument("--disable-gpu")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Open GitHub login page
    driver.get("https://www.hsbc.co.in/loans/products/personal/")

    # # Find the username and password input fields
    # username_input = driver.find_element(By.ID, "login_field")
    # password_input = driver.find_element(By.ID, "password")

    # # Enter your credentials
    # username_input.send_keys(USERNAME)
    # password_input.send_keys(PASSWORD)

    # # Find and click the login button
    # login_button = driver.find_element(By.NAME, "commit")
    # login_button.click()

    # Wait for a while to let the login process complete
    time.sleep(2)

    print("Let's say Monitoring started or Tracking .... ")

    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    print(driver.execute_script("return document.body.scrollWidth"), total_height)
    # Initialize the stitched image
    stitched_image = Image.new('RGB', (driver.execute_script("return document.body.scrollWidth"), total_height))

    # Scroll and capture screenshots
    offset = 0
    while offset < total_height:
        driver.execute_script(f"window.scrollTo(0, {offset});")
        delay=0.001
        time.sleep(delay)  # Allow some time for scrolling
        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(io.BytesIO(screenshot))
        
        stitched_image.paste(screenshot, (0, offset))
        offset += viewport_height

    # Save the final stitched image
    stitched_image_path = f"sele_full_page_screenshot_{delay}.png"
    stitched_image.save(stitched_image_path)


finally:
    # Quit the driver
    driver.quit()

