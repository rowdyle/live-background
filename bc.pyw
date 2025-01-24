import sys
import cv2
import ctypes
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5.QtGui import QPixmap, QImage

name = "C:/Users/rowdy/Videos/background/d2.mp4"  # Path to your video
x_offset = 0  # Only if there is an offset
y_offset = 0
time_wait_ml = 15
screen_off_time = 600 #secends

class VideoPlayer(QMainWindow):
    def __init__(self, video_path, time_wait_ml, x_offset=0, y_offset=0):
        super().__init__()

        # Variables for all the functions
        self.user32 = ctypes.windll.user32  # shortcut
        self.FindWindowExW = self.user32.FindWindowExW  # shortcut
        self.bacid = list()
        self.a = list()
        self.a2 = list()

        # Read the video file
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print("Error: Could not open video.")
            return

        # Get all screens
        self.app = QApplication.instance()
        self.screens = QApplication.screens()
        self.labels = []

        # Calculate the total width and height across all screens
        self.total_width = sum([screen.geometry().width() for screen in self.screens])
        self.total_height = sum([screen.geometry().height() for screen in self.screens])
        self.xgap = abs(min([screen.geometry().x() for screen in self.screens]))
        self.ygap = abs(min([screen.geometry().y() for screen in self.screens]))

        # Resize the QMainWindow to cover all monitors
        self.resize(self.total_width, self.total_height )
        self.move(0, 0)  # Position the window at the top-left corner

        # Create a QLabel for each screen
        x = 0
        for screen in self.screens:
            label = QLabel(self)
            screen_geometry = screen.geometry()
            label.resize(self.total_width, self.total_height)
            if screen_geometry.x() < 0:
                x = 0
            else:
                x = self.xgap + screen_geometry.x()

            if screen_geometry.y() < 0:
                y = 0 - int(screen_geometry.height()/2) 
            else:
                y = self.ygap + screen_geometry.y() - int(screen_geometry.height()/2)

            label.move(x ,y) 
            self.labels.append(label)

        self.setWindowFlags(Qt.FramelessWindowHint)  # No border

        # Set the background window
        self.set_background_window(x_offset, y_offset)

        # Create the video update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)  # Timer to update the video frame
        self.timer.start(time_wait_ml)

        self.show()

    def update(self):
        ret, frame = self.cap.read()  # Read the next frame

        if ret:
            # Resize the frame for each screen
            for label, screen in zip(self.labels, self.screens):
                screen_geometry = screen.geometry()
                frame_height, frame_width, _ = frame.shape

                # Scale the frame to fit the screen
                scale_width = screen_geometry.width() / frame_width
                scale_height = screen_geometry.height() / frame_height

                scale_factor = max(scale_width, scale_height)
                new_width = int(frame_width * scale_factor)
                new_height = int(frame_height * scale_factor)

                resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

                # Convert to QPixmap and set to QLabel
                pixmap = QPixmap(frame_to_pixmap(resized_frame))
                label.setPixmap(pixmap)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart the video

    def set_background_window(self, x_offset, y_offset):
        """Set the WorkerW window as a background window and make it a child of the main window."""
        FindWindowExW = self.user32.FindWindowExW  # shortcut
        hwnd = None

        # Get the WorkerW background window
        while True:
            hwnd = FindWindowExW(None, hwnd, "WorkerW", None)
            if hwnd:
                self.bacid.append(hwnd)
            else:
                break  # Break when no more windows are found

        # Set the parent of the background window to the QMainWindow (using SetParent)
        # Adjust window position and size
        self.user32.SetParent(int(self.winId()), self.bacid[-1])
        print("start all good ;)")

    def on_size(self, hwnd):
        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)
            ]

        user32 = ctypes.windll.user32

        # Get working area (screen excluding taskbar)
        rect = RECT()
        if not user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):  # SPI_GETWORKAREA
            return False

        work_width = rect.right - rect.left - 100
        work_height = rect.bottom - rect.top - 100

        # Get the rectangle of the window
        window_rect = RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(window_rect)):
            return False

        # Calculate window dimensions
        window_width = window_rect.right - window_rect.left
        window_height = window_rect.bottom - window_rect.top

        # Check if the window matches the working area
        is_fullscreen = (window_width > work_width and window_height > work_height)
        return is_fullscreen

    def get_idle_time(self):
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint),
                        ("dwTime", ctypes.c_uint)]

        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        millis /= 1000.0  # Convert to seconds

        if millis >= screen_off_time:
            return True
        return False

    def on_window(self):
        # Get the current foreground window
        top = ctypes.windll.user32.GetForegroundWindow()

        # Try to get information about the display
        if self.get_idle_time():
            False

        # Check if it's not fullscreen
        if not self.on_size(top):
            return True

        # Check if the window is in one of your tracked lists
        for window_list in [self.bacid, self.a, self.a2]:
            if top in window_list:
                return True

        return False


    def update_frame(self):
        if len(self.bacid) != 0:
            if self.on_window():
                self.update()
        else:
            self.update()

def frame_to_pixmap(frame):
    """Convert an OpenCV frame to a QPixmap."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    height, width, channels = frame_rgb.shape
    bytes_per_line = channels * width
    q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(q_image)

#---------------------------------------------------------------------------------
def main(video_path, time_wait_ml, x_offset=0, y_offset=0):
    app = QApplication(sys.argv)
    player = VideoPlayer(video_path, time_wait_ml, x_offset, y_offset)  # Make the window with PyQt5
    sys.exit(app.exec_())
#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main(name, time_wait_ml, x_offset, y_offset)  # Adjust these values as needed
