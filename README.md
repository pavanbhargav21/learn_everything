import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import time

def capture_window(hwnd, x, y, width, height):
    try:
        # Get the window's device context
        window_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(window_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        
        # Create a bitmap to hold the screenshot
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(bitmap)
        
        # Copy the window's device context to the bitmap
        save_dc.BitBlt((0, 0), (width, height), mfc_dc, (x, y), win32con.SRCCOPY)
        
        # Save the bitmap to a file
        bitmap_info = bitmap.GetInfo()
        bitmap_str = bitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bitmap_info['bmWidth'], bitmap_info['bmHeight']),
            bitmap_str, 'raw', 'BGRX', 0, 1
        )
        
        return img
        
    finally:
        # Clean up resources
        try:
            if save_dc:
                save_dc.DeleteDC()
            if bitmap:
                win32gui.DeleteObject(bitmap.GetHandle())
            if mfc_dc:
                mfc_dc.DeleteDC()
            if window_dc:
                win32gui.ReleaseDC(hwnd, window_dc)
        except Exception as e:
            print(f"Error during resource cleanup: {e}")

def scroll_window(hwnd, direction, amount):
    # Scroll the window content in the specified direction
    if direction == 'vertical':
        win32gui.SendMessage(hwnd, win32con.WM_VSCROLL, win32con.SB_LINEDOWN * amount, None)
    elif direction == 'horizontal':
        win32gui.SendMessage(hwnd, win32con.WM_HSCROLL, win32con.SB_LINERIGHT * amount, None)

def is_window_scrollable(hwnd):
    # Get the window style
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    
    # Check if vertical or horizontal scroll bars are present
    has_vertical_scroll = style & win32con.WS_VSCROLL
    has_horizontal_scroll = style & win32con.WS_HSCROLL
    print(f"It is {has_vertical_scroll} and {has_horizontal_scroll}")
    return has_vertical_scroll or has_horizontal_scroll

def capture_full_window(hwnd):
    try:
        # Get the window's dimensions
        left, top, right, bot = win32gui.GetClientRect(hwnd)
        width = right - left
        height = bot - top
        
        # Initial capture
        full_image = capture_window(hwnd, 0, 0, width, height)
        
        if is_window_scrollable(hwnd):
            # Scrollable content capture
            scroll_amount = 100  # Adjust based on scrolling sensitivity
            images = [full_image]
            while True:
                scroll_window(hwnd, 'vertical', scroll_amount)
                img = capture_window(hwnd, 0, 0, width, height)
                if img.tobytes() == images[-1].tobytes():
                    break  # No more new content to capture
                images.append(img)
            
            # Stitch images together
            total_height = sum(image.height for image in images)
            full_img = Image.new('RGB', (width, total_height))
            y_offset = 0
            for img in images:
                full_img.paste(img, (0, y_offset))
                y_offset += img.height
        else:
            # Non-scrollable content capture
            full_img = full_image
        
        # Save the stitched image
        full_img.save('hello__full_screenshot.png')
    
    except Exception as e:
        print(f"Error during capture: {e}")

def main():
    try:
        # Get the handle of the currently active window
        time.sleep(5)
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            capture_full_window(hwnd)
        else:
            print("No active window found.")
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
