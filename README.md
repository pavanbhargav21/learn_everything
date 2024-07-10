import win32gui
import win32ui
import win32con
import win32api
from ctypes import windll
import ctypes

def capture_full_window(hwnd):
    # Get the window dimensions
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bot - top

    # Create a device context for the entire window
    hwindc = win32gui.GetWindowDC(hwnd)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()

    # Create a bitmap compatible with the window's device context
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)

    # Use PrintWindow to copy the entire window to the bitmap
    result = windll.user32.PrintWindow(hwnd, memdc.GetSafeHdc(), 0)
    if result == 0:
        raise Exception("PrintWindow failed")

    # Save the bitmap to a file
    bmp.SaveBitmapFile(memdc, 'hello_full_window_screenshot.bmp')

    # Release resources
    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

# Get the handle of the active window
hwnd = win32gui.GetForegroundWindow()
if hwnd:
    capture_full_window(hwnd)
else:
    print("No active window found")
