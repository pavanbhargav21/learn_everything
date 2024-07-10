There are several libraries in Python that you can use to capture an image of a present window with full high definition. Here are a few popular ones:

1. **PyAutoGUI**: A cross-platform GUI automation library that allows you to control the mouse and keyboard, as well as capture screenshots.

   ```python
   import pyautogui
   screenshot = pyautogui.screenshot()
   screenshot.save('screenshot.png')
   ```

2. **Pillow**: A Python Imaging Library (PIL) fork that adds image processing capabilities. Often used in combination with other libraries to capture and process screenshots.

   ```python
   from PIL import ImageGrab
   screenshot = ImageGrab.grab()
   screenshot.save('screenshot.png')
   ```

3. **mss**: A cross-platform library specifically designed for capturing screenshots. It's known for being fast and lightweight.

   ```python
   import mss
   with mss.mss() as sct:
       sct.shot(output='screenshot.png')
   ```

4. **opencv-python**: A library for computer vision that can be used for image capture and processing.

   ```python
   import cv2
   import numpy as np
   from PIL import ImageGrab

   img = ImageGrab.grab()
   img_np = np.array(img)
   frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
   cv2.imwrite('screenshot.png', frame)
   ```

5. **PyQt5 or PySide2**: If you are working with a GUI application built with these libraries, they provide methods to capture screenshots of their windows.

   ```python
   from PyQt5.QtWidgets import QApplication
   from PyQt5.QtGui import QScreen
   import sys

   app = QApplication(sys.argv)
   screen = QApplication.primaryScreen()
   screenshot = screen.grabWindow(0)
   screenshot.save('screenshot.png', 'png')
   ```

6. **pygetwindow**: A library for getting information about windows and interacting with them. It can be used in combination with other libraries like Pillow or mss for capturing specific windows.

   ```python
   import pygetwindow as gw
   from PIL import ImageGrab

   window = gw.getWindowsWithTitle('Window Title')[0]
   bbox = window.left, window.top, window.right, window.bottom
   screenshot = ImageGrab.grab(bbox=bbox)
   screenshot.save('screenshot.png')
   ```

Each of these libraries has its strengths and specific use cases, so the best choice depends on your particular requirements and the environment in which you are working.