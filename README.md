import win32gui
import win32ui
import win32con
import win32api
import time

def capture_active_window():
    try:
        # Get the handle to the active window
        hwnd = win32gui.GetForegroundWindow()

        if hwnd:
            print("Active window handle retrieved successfully.")

            # Get the entire window dimensions
            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bot - top
            print(f"Entire window dimensions: ({left}, {top}) to ({right}, {bot})")
            print(f"Entire window size: {width} x {height}")

            # Create a device context for the entire window
            hwindc = win32gui.GetWindowDC(hwnd)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()

            # Create a bitmap compatible with the window's device context
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, width, height)
            memdc.SelectObject(bmp)

            # Add a delay before capturing
            time.sleep(1)  # Adjust as needed (e.g., 1 second)

            # Perform a BitBlt operation to copy the window content to the bitmap
            if not memdc.BitBlt((0, 0), (width, height), srcdc, (0, 0), win32con.SRCCOPY):
                raise RuntimeError("BitBlt operation failed.")
            print("BitBlt operation successful.")

            # Save the bitmap to a file
            bmp.SaveBitmapFile(memdc, 'full_window_screenshot.bmp')
            print("Bitmap saved successfully.")

            # Release resources
            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())

            print("Resources released.")
        else:
            print("No active window found.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

# Example usage:
capture_active_window()
