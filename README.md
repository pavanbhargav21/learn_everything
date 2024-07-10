import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 9  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
import time
import threading
import pyautogui
import pygetwindow

# Function to find and activate the active Visual Studio Code window
def find_active_vscode_window():
    vscode_window = pygetwindow.getWindowsWithTitle('Visual Studio Code')[0]
    vscode_window.activate()
    return vscode_window

# Function to continuously scroll and capture content of the active window
def scroll_and_capture_content():
    vscode_window = find_active_vscode_window()
    total_lines = 1200  # Example: Total lines in the active window
    visible_lines = 90  # Example: Number of visible lines in the window
    
    # Calculate how many scrolls are needed to capture all lines
    num_scrolls = (total_lines // visible_lines) + 1
    
    for _ in range(num_scrolls):
        # Scroll down (adjust as needed)
        pyautogui.scroll(-visible_lines)
        
        # Capture screenshot of the entire window
        screenshot = pyautogui.screenshot(region=vscode_window.box)
        screenshot.save(f'vscode_capture_scroll{_}.png')  # Example: Save screenshot
    
        # Adjust sleep time as needed to control scroll rate
        time.sleep(1)  # Adjust as needed

# Function to run scrolling and capturing in a separate thread
def run_scroll_capture_thread():
    scroll_thread = threading.Thread(target=scroll_and_capture_content)
    scroll_thread.daemon = True  # Thread will terminate when main program exits
    scroll_thread.start()

# Main function (simulating your work in Visual Studio Code)
def main():
    # Simulate working in Visual Studio Code
    while True:
        print("Writing code in Visual Studio Code...")
        time.sleep(5)  # Simulate work interval (adjust as needed)

if __name__ == "__main__":
    # Start scrolling and capturing in a separate thread
    run_scroll_capture_thread()
    
    # Run main function (simulating work in Visual Studio Code)
    main()
