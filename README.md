import win32gui
import win32ui
import win32con
import win32api
import ctypes
from ctypes import wintypes
import sys
import os
import mss
import mss.tools
from PIL import Image
import time
time.sleep(5)
def debug_print(message):
    print(f"DEBUG: {message}")
    sys.stdout.flush()

def capture_window_ex(hwnd):
    # Get window dimensions
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # Get window DC and create a memory DC
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # Create a bitmap and select it into the memory DC
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # Capture the window using PrintWindow
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    debug_print(f"PrintWindow result: {result}")

    # Convert the bitmap to a PIL Image
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    # Clean up
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img

def capture_active_window():
    try:
        debug_print("Starting capture process...")
        
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            debug_print("No active window found.")
            return

        debug_print(f"Active window handle: {hwnd}")
        window_text = win32gui.GetWindowText(hwnd)
        debug_print(f"Active window title: {window_text}")

        # Method 1: Custom PrintWindow capture
        debug_print("Attempting custom PrintWindow capture...")
        img = capture_window_ex(hwnd)
        img.save('custom_printwindow_screenshot.png')
        debug_print(f"Custom PrintWindow screenshot saved. Size: {os.path.getsize('custom_printwindow_screenshot.png')} bytes")

        # Method 2: MSS capture
        debug_print("Attempting MSS capture...")
        with mss.mss() as sct:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            monitor = {"top": top, "left": left, "width": right-left, "height": bottom-top}
            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output="mss_screenshot.png")
        debug_print(f"MSS screenshot saved. Size: {os.path.getsize('mss_screenshot.png')} bytes")

        # Method 3: Win32 BitBlt (for comparison)
        debug_print("Attempting Win32 BitBlt capture...")
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)
        
        result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
        if result:
            debug_print("BitBlt successful.")
            saveBitMap.SaveBitmapFile(saveDC, 'bitblt_screenshot.bmp')
            debug_print(f"BitBlt screenshot saved. Size: {os.path.getsize('bitblt_screenshot.bmp')} bytes")
        else:
            debug_print("BitBlt failed.")

        # Clean up
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

    except Exception as e:
        debug_print(f"Error occurred: {str(e)}")
        import traceback
        debug_print(traceback.format_exc())

if __name__ == "__main__":
    capture_active_window()
    input("Press Enter to exit...")
