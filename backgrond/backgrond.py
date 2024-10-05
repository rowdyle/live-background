import sys
import cv2
import ctypes
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QLabel
from PyQt5.QtGui import QPixmap, QImage

name = "your/path/to/the/file" # change it to your vidue
x_offset=0 # only if there is an offset
time_wait_ml = 30

class VideoPlayer(QMainWindow):
    def __init__(self, video_path,time_wait_ml, x_offset=0, y_offset=0):
        super().__init__()

        #---------------------------------------------------------
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():                     #read the mp4 + debug
            print("Error: Could not open video.")
            return
        #----------------------------------------------------------

        self.setWindowFlags(Qt.FramelessWindowHint)  # make it frameless 

        #----------------------------------------------------------
        screen_rect = QDesktopWidget().screenGeometry()
        self.wigit = QLabel(self)                                       #imge seter
        self.wigit.resize(screen_rect.width(),screen_rect.height())
        #----------------------------------------------------------
        self.bacid = list()
        self.user32 = ctypes.windll.user32         #shortcut
        self.FindWindowExW = self.user32.FindWindowExW  #shortcut
        self.vin = None
        self.a = list()
        self.a2= list()

        while True:
            self.vin = self.FindWindowExW(None, self.vin, "Shell_TrayWnd", None) #found the next window with the class name "WorkerW after hwnd 
            if self.vin:
                self.a.append(self.vin)
            else:       
                break   
        while True:
            self.vin = self.FindWindowExW(None, self.vin, "Windows.UI.Core.CoreWindow", None) #found the next window with the class name "WorkerW after hwnd 
            if self.vin:
                self.a2.append(self.vin)
            else:       
                break

        self.update_frame()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)       #timer also make it loop
        self.timer.start(time_wait_ml) 

        #----------------------------------------------------------

        self.wallPaper(x_offset, y_offset)

        self.show()

    def update_frame(self):
        top = ctypes.windll.user32.GetForegroundWindow()

        if len(self.bacid) != 0:
            if top == self.a[-1] or top == self.bacid[-2] or top == self.a2[2]:
                ret, frame = self.cap.read() # Read the next frame
                #---------------------------------------------------------
                if ret:
                    self.wigit.setPixmap(QPixmap(frame_to_pixmap(frame)))    # convert the frame to pixmap for the pyqt5
                else:#-----------------------------------------------------
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) #go back to the start of the vidue
        else:
            ret, frame = self.cap.read() # Read the next frame
            #---------------------------------------------------------
            if ret:
                self.wigit.setPixmap(QPixmap(frame_to_pixmap(frame)))    # convert the frame to pixmap for the pyqt5
            else:#-----------------------------------------------------
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) #go back to the start of the vidue



    def wallPaper(self, x_offset, y_offset):
        #----------------------------------------------------------------------------------
        FindWindowExW = self.user32.FindWindowExW  #shortcut
        hwnd = None

        while True:
            hwnd = FindWindowExW(None, hwnd, "WorkerW", None) #found the next window with the class name "WorkerW after hwnd 
            if hwnd:
                self.bacid.append(hwnd)
            else:       
                break # if there is no window next its get 0 and that make it break 

        screen_rect = QDesktopWidget().screenGeometry()
        self.resize(screen_rect.width(), screen_rect.height())          #center and size
        self.user32.SetWindowPos(self.bacid[-1], 0, x_offset, y_offset, screen_rect.width(),screen_rect.height(), 0) 
        #----------------------------------------------------------------------------------
        self.user32.SetParent(int(self.winId()), self.bacid[-1])      #make it a child of the background
        #----------------------------------------------------------------------------------
                
def frame_to_pixmap(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    height, width, channels = frame_rgb.shape
    bytes_per_line = channels * width
    q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(q_image)

#---------------------------------------------------------------------------------
def main(video_path,time_wait_ml, x_offset=0, y_offset=0):
    app = QApplication(sys.argv)
    player = VideoPlayer(video_path,time_wait_ml, x_offset, y_offset) # make the window with pyqt5
    sys.exit(app.exec_())
#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main(name,time_wait_ml, x_offset, y_offset=0)  # Adjust these values as needed

