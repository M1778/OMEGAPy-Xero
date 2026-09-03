# UNUSED - kept for reference
# FAILED BECAUSE OF LACK OF MOTIVATION -> LAZYNESS PROBABLY ITS FAIR BECAUSE NOBODY PAID ME TO DO THIS
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from chatwin import ChatWindow
from login import LoginPage
from threading import Thread
from pathlib import Path
import speech_recognition as sr
import pyaudio
import threading
import multiprocessing
import difflib
import pyttsx3
import numpy as np
import random
import math
import time
import sys
import json

global MAIN_WINDOW_OBJECT, MAIN_WINDOW_AVAILABLE
MAIN_WINDOW_AVAILABLE=False
MAIN_WINDOW_OBJECT=None

stop_flag = threading.Event()
keyword = "camel"

engine = pyttsx3.init()
engine.setProperty("rate",175)
engine.setProperty("voice",engine.getProperty("voices")[1].id)
r=sr.Recognizer()

config = json.load(open(str(Path(__file__).parent.joinpath("settings.json")),'r'))

class AudioCaptureThread(QThread):
    audio_data_signal = pyqtSignal(np.ndarray)  # Signal to send audio data

    def __init__(self, sample_rate=44100, chunk_size=1024):
        super().__init__()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.running = True
    def run(self):
        """Capture audio in a loop using PyAudio."""
        try:
            audio_interface = pyaudio.PyAudio()
            stream = audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            while self.running:
                # Read audio data
                audio_chunk = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(audio_chunk, dtype=np.int16)

                # Normalize audio data
                normalized_data = audio_data / np.iinfo(np.int16).max

                # Emit normalized audio data
                self.audio_data_signal.emit(normalized_data)

            # Stop stream
            stream.stop_stream()
            stream.close()
            audio_interface.terminate()

        except:
            print(f"Error in audio thread.")

    def stop(self):
        """Stop the audio capture loop."""
        self.running = False
        self.wait()
def calculate_sizes(x,y):
    #return round(x*0.26049),round(y*0.69449)
    return 500,750
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setFixedSize(*calculate_sizes(1,2)) #*calculate_sizes(win32api.GetSystemMetrics(0),win32api.GetSystemMetrics(1)))
        font = QtGui.QFont()
        font.setFamily(config['General']['Font'])
        self.setFont(font)
        self.primary_color = config['General']['PrimaryColor']
        self.secondary_color = config['General']['SecondaryColor']
        self.bkg_image = config['General']["BackgroundImage"]
        self.btn_bkg_image = config['General']["MainButtonBackgroundImage"]
        self.text_color = config['General']['TextColor']
        self.setStyleSheet("    * {\n"
f"color: {self.text_color};\n"
f"border-color:{self.secondary_color};\n"
"\n"
"}\n"
"QWidget{\n"
"background: none;\n"
"background-repeat: no-repeat;\n"
"}\n"
"QTextBrowser{background:none}\n"
"QPushButton {    \n"
"    text-decoration: none;\n"
"    border-radius: 15px;\n"
f"    background-color: {self.primary_color};\n"
"    border: 1px solid rgba(255, 255, 255, 0.5);\n"
"    color: rgba(255, 255, 255, 0.8);\n"
"    font-size: 14px;\n"
"    letter-spacing: 2px;\n"
"    text-transform: uppercase;\n"
"    background: none;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(255, 255, 255, 0.2);\n"
"}\n"
"QPushButton:before {\n"
"  background: none;\n"
"  border: 4px solid #fff;\n"
"  content: \"\";\n"
"  display: block;\n"
"  position: absolute;\n"
"  pointer-events: none;\n"
"}\n"
"\n"
"QPushButton:after{\n"
"content: \'\';\n"
"  position: absolute;\n"
"  inset: 0;\n"
"  border-radius: inherit;\n"
"  opacity: 0.6;\n"
"}\n"
"\n"
"QLabel {\n"
"    background:transparent;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.centralwidget.setObjectName("centralwidget")
        self.pushtotalk = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushtotalk.setGeometry(QtCore.QRect(130, 60, 250, 250))
        self.pushtotalk_secondstylesheet = """
        QPushButton {
            border-radius: 125%;
            border-width: 5px;
            position: relative;
            border-style: solid;
            border-color: """ +self.primary_color+ """;  /* Purple border */
            background-color: """ + self.secondary_color+""";  /* Dark background */
            color: #9461fd;  /* Purple text */
            font-size: 18px;
            padding: 10px 20px;
            text-align: center;
        }

        QPushButton:hover {
            border-color: """ + self.secondary_color +""";  /* Cyan border on hover */
            color: #00ffff;  /* Cyan text color on hover */
            background-color: #3a3a3a;  /* Darker background on hover */
        }

        QPushButton:pressed {
            background-color: #00ffff;  /* Cyan background when pressed */
            color: #333;  /* Dark text on cyan background */
            border-color: #9461fd;  /* Original purple border when pressed */
        }
    """
        self.pushtotalk_defaultstylesheet="""QPushButton {
    border-radius: 125%;
   border-width: 5px;
position:relative;
    border-style: solid;
    border-color:"""+self.primary_color+""";
    subcontrol-position: right center;
    subcontrol-origin: padding;
}
"""
        self.pushtotalk.setStyleSheet(self.pushtotalk_secondstylesheet)
        self.pushtotalk.setObjectName("pushtotalk")
        self.is_talking = False
        self.waveform_offset = 0
        self.wavefrom_amplitude = 20
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)
        self.wave_amplitude = 10  # Height of waveform peaks/  maximum:20
        self.num_points = 360  # Number of points in the circle
        self.frequency = 10  # Number of waveform oscillations
        self.audio_data = np.zeros(360)
        self.audio_thread = AudioCaptureThread()
        self.audio_thread.audio_data_signal.connect(self.update_audio_data)
        self.audio_thread.start()
        # self.pushtotalk_dropshadow = self.create_dropshadow(self.pushtotalk,QColor("#4003e6"),100,10,10)
        # self.pushtotalk.setGraphicsEffect(self.pushtotalk_dropshadow)
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(self.secondary_color))  # Cyan glow
        shadow_effect.setOffset(0, 0)  # No offset, shadow stays centered
        shadow_effect.setBlurRadius(155)  # How spread out the glow is

        # Apply shadow effect to button
        self.pushtotalk.setGraphicsEffect(shadow_effect)
        self.pushtotalk.pressed.connect(self.istalking)
        self.textresponse = QtWidgets.QTextBrowser(parent=self.centralwidget)
        self.textresponse.setGeometry(QtCore.QRect(80, 370, 350, 250))
        self.textresponse.setStyleSheet("""
    QTextBrowser {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2a1d43, stop:1 #3b2b64);
        color: #b1a1d9;
        font-family: 'Arial', sans-serif;
        font-size: 14px;
        line-height: 1.6;
        border: 2px solid """+self.primary_color + """;
        border-radius: 15px;
        padding: 15px;
        text-shadow: 0px 0px 5px rgba(148, 97, 253, 1), 0px 0px 10px rgba(148, 97, 253, 0.8);
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
    }

    QTextBrowser:hover {
        border-color: #a580f7;
        color: #9461fd;
    }

    QTextBrowser QScrollBar {
        background: #3b2b64;
        width: 12px;
        border-radius: 6px;
    }

    QTextBrowser QScrollBar::handle {
        background: #9461fd;
        border-radius: 6px;
    }

    QTextBrowser QScrollBar::handle:hover {
        background: #a580f7;
    }

    QTextBrowser QScrollBar::add-line, QTextBrowser QScrollBar::sub-line {
        border: none;
        background: none;
    }

    QTextBrowser QScrollBar::add-page, QTextBrowser QScrollBar::sub-page {
        background: none;
    }

    QTextBrowser:focus {
        border-color: #9461fd;
    }
""")
        self.textresponse.setObjectName("textresponse")
        self.switchtotextmodebtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.switchtotextmodebtn.setGeometry(QtCore.QRect(170, 650, 171, 51))
        self.switchtotextmodebtn.setObjectName("switchtotextmodebtn")
        self.switchtotextmodebtn.pressed.connect(self.switch_)
        self.credits = QtWidgets.QLabel(parent=self.centralwidget)
        self.credits.setGeometry(QtCore.QRect(10, 720, 91, 16))
        self.credits.setStyleSheet("")
        self.credits.setObjectName("credits")
        self.setCentralWidget(self.centralwidget)
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        QShortcut(QKeySequence('a'),self,self.job)
    # def paintEvent(self,event):
    #     painter = QPainter(self)
    #     painter.setPen(QPen(QColor(255,0,0),2))
    #     points = []
    #     button_rect = self.pushtotalk.geometry()
        
    #     for i in range(button_rect.width()):
    #         x = button_rect.x() + i
    #         y = button_rect.y() + button_rect.height()//2 + self.wavefrom_amplitude * math.sin(i/10+self.waveform_offset)
    #         points.append(QPoint(x,round(y)))
        
    #     painter.drawPolyline(points)
    #     self.waveform_offset+=0.1
    def job(self):
        ...
    def switch_(self):
        self.chatwin=ChatWindow()
        self.chatwin.load_messages(message_list=[])
        self.chatwin.configure_on_close(self)
        self.chatwin.show()
        self.setHidden(True)
        self.setDisabled(True)
    def update_audio_data(self, new_audio_data):
        """Receive audio data from the thread and update the waveform."""
        # Resample to 360 points to match the waveform size
        self.audio_data = np.interp(
            np.linspace(0, len(new_audio_data), 360),
            np.arange(len(new_audio_data)),
            new_audio_data
        )
    def draw_straight_waveform(self, painter):
        """Draw a more noise-sensitive straight-line waveform below the button."""
        # Get button geometry
        button_rect = self.pushtotalk.geometry()
        button_center = button_rect.center()
        button_radius = button_rect.width() // 2
        wave_line_y = button_center.y() + button_radius + 30  # Y position below the button

        # Define line properties (adjust thickness based on average amplitude)
        average_amplitude = np.mean(np.abs(self.audio_data))
        line_thickness = max(2, int(average_amplitude * 10))
        painter.setPen(QPen(QColor(self.primary_color), line_thickness))  # Neon cyan line color

        # Create the waveform path in a straight line below the button
        waveform = QPolygonF()

        # Calculate points for the waveform with increased noise sensitivity
        if self.is_talking:
            sensitivity_factor = 250  # Increase this factor for higher waves
        else:
            sensitivity_factor=0
        width = self.width()  # Get the width of the window
        num_points = width  # Ensure that we plot points for each pixel across the window

        # Calculate points for the waveform
        for x in range(num_points):  # Loop through every pixel in the window width
            amplitude = self.audio_data[int(x % len(self.audio_data))] * sensitivity_factor  # Scaling for visibility
            y = wave_line_y + amplitude  # Vertical position based on amplitude
            waveform.append(QPointF(np.random.normal(x), y))

        # Draw the waveform line
        painter.drawPolyline(waveform)
    def paintEvent(self, event):
        """Paint the animated waveform around the button."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        background_pixmap = QPixmap(str(Path(__file__).parent.joinpath("data/darkpurpleback.jpg")) if config['General']['BackgroundImage'].lower()=='default' else config['General']['BackgroundImage'])  # Replace with your image path
        if background_pixmap.isNull():
            painter.fillRect(self.rect(), QColor(50, 50, 50))  # Solid gray fallback
        else:
            painter.drawPixmap(self.rect(), background_pixmap)
        painter.drawPixmap(self.rect(), background_pixmap)
        if self.is_talking:
            # Get button geometry
            button_rect = self.pushtotalk.geometry()
            button_center = button_rect.center()
            button_radius = button_rect.width() // 2
            wave_radius = button_radius  # Distance from the button
            if len(self.audio_data) < 360:
                print("Error: Insufficient audio data.")
                return
            # Create the waveform path
            waveform = QPolygonF()
            for angle in range(360):
                theta = np.radians(angle)
                amplitude = self.audio_data[angle] * 200  # Scaling for visibility
                x = button_center.x() + (wave_radius + amplitude) * np.cos(theta)
                y = button_center.y() + (wave_radius + amplitude) * np.sin(theta)
                waveform.append(QPointF(round(x), round(y)))

            # Ensure the path closes by appending the first point to the end
            waveform.append(waveform[0])
            # 1. Neon-style Gradient: Dark purple to dark blue with glowing effect
            gradient = QLinearGradient(random.randint(100,500), random.randint(100,500), random.randint(100,500), random.randint(100,500))  # Dummy gradient direction
            gradient.setColorAt(1.0, QColor(50, 0, 50))    # Dark Purple
            gradient.setColorAt(0.8, QColor(75, 0, 130))   # Indigo
            gradient.setColorAt(0.6, QColor(0, 0, 255))    # Dark Blue
            gradient.setColorAt(0.5, QColor(0, 128, 255))  # Sky Blue
            gradient.setColorAt(0.4, QColor(0, 255, 255))  # Cyan
            gradient.setColorAt(0.3, QColor(0, 255, 128))  # Mint Green
            gradient.setColorAt(0.2, QColor(0, 255, 0))    # Bright Green
            gradient.setColorAt(0.1, QColor(255, 255, 0))  # Yellow
            gradient.setColorAt(0.05, QColor(255, 128, 0)) # Orange
            gradient.setColorAt(0.0, QColor(255, 0, 0))    # Bright Red


            pen = QPen(QBrush(gradient), max(2, int(np.mean(np.abs(self.audio_data)) * 10)))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)

            # 3. Draw the waveform lines
            painter.drawPolyline(waveform)

            # 4. Fill the area between the button and waveform with a semi-transparent color
            wave_fill = QPolygonF()
            wave_fill.append(QPointF(button_center.x(), button_center.y()))  # Start from center
            wave_fill += waveform
            wave_fill.append(QPointF(waveform[0].x(), waveform[0].y()))  # Close the polygon
            painter.setBrush(QColor(255, 0, 0, 50))  # Semi-transparent red
            painter.setPen(Qt.PenStyle.NoPen)  # No border for the fill
            painter.drawPolygon(wave_fill)
        self.draw_straight_waveform(painter)

    def closeEvent(self, event):
        """Ensure the audio thread is stopped when the window closes."""
        self.audio_thread.stop()
        super().closeEvent(event)
    def create_dropshadow(self,parent,color:QColor,blur:float,x:float,y:float):
        dropshadow = QGraphicsDropShadowEffect(parent)
        dropshadow.setColor(color)
        dropshadow.setBlurRadius(blur)
        dropshadow.setXOffset(x)
        dropshadow.setYOffset(y)
        return dropshadow
    def istalking(self):
        if self.is_talking == False:
            self.audio_text = ""
            self.is_talking = True
            self.tt=Thread(target=listen_and_set,args=(self,))
            self.tt.start()
            time.sleep(0.5)
            self.pushtotalk.setText("Listening...")
        else:
            self.is_talking = False
    def retranslateUi(self,obj):
        _translate = QtCore.QCoreApplication.translate
        obj.setWindowTitle(_translate("MainWindow", "OMEGAPy-SoreUI"))
        obj.pushtotalk.setText(_translate("MainWindow", "PUSH TO TALK"))
        obj.switchtotextmodebtn.setText(_translate("MainWindow", "Switch to text"))
        obj.credits.setText(_translate("MainWindow", "Made by M1778"))

def listen_and_set(self_):
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source,0.5)
        audio_text = r.listen(source)
        self_.is_talking = False
        self_.pushtotalk.setText("Processing...")
        try:
            self_.audio_text = r.recognize_google(audio_text)
        except sr.UnknownValueError:
            self_.pushtotalk.setText("Resetting...")
            Thread(target=speak,args=(self_.audio_text,)).start()
            self_.audio_text = ""
            self_.is_talking = False
            self_.pushtotalk.setText("PUSH TO TALK")
            return
        print(self_.audio_text)
        Thread(target=speak,args=(self_.audio_text,)).start()
        self_.pushtotalk.setText("PUSH TO TALK")
    return self_.audio_text

def loop_in_process():
    global MAIN_WINDOW_OBJECT, MAIN_WINDOW_AVAILABLE
    COPY_MAINWINDOW = None
    while not stop_flag.is_set() and MAIN_WINDOW_AVAILABLE and MAIN_WINDOW_OBJECT != None:
        if COPY_MAINWINDOW == None:COPY_MAINWINDOW = MAIN_WINDOW_OBJECT
        try:
            with sr.Microphone() as mic:
                r.adjust_for_ambient_noise(mic,0.2)
                print("GOING TO LISTEN")
                audio = r.listen(mic,timeout=3,phrase_time_limit=5)
                print("LISTEN COMPLETED, NOW RECOGNIZING")
                text = r.recognize_google(audio)
                text=text.lower()
                print(text)
                if text == "stop":
                    stop_flag.set()
                    exit(0)
                if difflib.SequenceMatcher(None,keyword,text).ratio() > 0.5:
                    print("\a")
                    COPY_MAINWINDOW.pushtotalk.setText("Listening...")
                    COPY_MAINWINDOW.is_talking=True
                    print("LISTE_AND_SET")  
                    listen_and_set(COPY_MAINWINDOW)
        except Exception as err:print(f"Warning: An error occured while trying to be in the main listening loop.\n{err}")

def speak(text:str):
    try:
        engine.endLoop()
    except:...
    try:
        engine.stop()
    except:...
    if text == "":
        return
    engine.setProperty("rate",175)
    engine.setProperty("voice",engine.getProperty("voices")[1].id)
    engine.say(text)
    try:
        engine.runAndWait()
    except RuntimeError:
        speak(text)
if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    p = multiprocessing.Process(target=loop_in_process)
    p.start()
    
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())

    p.terminate()
    p.join()