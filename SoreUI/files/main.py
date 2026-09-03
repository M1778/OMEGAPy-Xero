# SORRY IF MY CODE IS MESSY
# I AM A MESSY PERSON MYSELF BUT I SWEAR I WRITE CLEAN WHEN I ENJOY WRITING SOMETHING YOU GET IT RIGHT?!
# MainWindow Rework for the third time after multiple fights with LLM that at last made me do all the work ofcourse
# I HATE LLMs and myself


# IMPORTS
import sys
import math
import random
import time
import numpy as np
import pyaudio
import xmanager
import json
from pathlib import Path
from settings import SettingsWindow,read_latest_config
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from omglib.llm import tools



# INITIALIZE INUSE TOOLS
tools.init_inuse_tools_import()

# CONFIG LAST UPDATE FUNCTION RETURN
config = lambda : read_latest_config()

# WHATEVER THIS IS 
def get_system_command(): # CHANGE LATER
    return {"role":"system","content":"You are a helpful assistant.\nAvoid using tool calls as much as possible only if user requests them and it's safe to use them.\n DO NOT USE TOOL CALLS FOR NORMAL CONVERSATION ONLY IF USER REQUESTS SOMETHING THAT REQUIRES TOOL CALL YOU ARE ALLOWED"}

# YEAH THIS ONE IS GPT
def create_dynamic_gradient(avg_amp, rect):
    """
    Create a dynamic linear gradient that shifts its hue based on the average amplitude.
    
    Parameters:
      avg_amp (float): The average amplitude (from 0 to 1).
      rect (QRectF): The area over which to define the gradient.
      
    Returns:
      QLinearGradient: A gradient that changes color based on avg_amp.
    """
    hue = int((avg_amp * 360) % 360)
    #COLORS
    color1 = QColor.fromHsv(hue, 255, 255)
    color2 = QColor.fromHsv(int(hue/random.randint(2,4)),random.randint(0,255),random.randint(0,255))
    color3 = QColor.fromHsv(int(hue/random.randint(2,4)),random.randint(0,255),random.randint(0,255))
    color4 = QColor.fromHsv(int(hue/random.randint(2,4)),random.randint(0,255),random.randint(0,255))
    color5 = QColor.fromHsv(int(hue/random.randint(2,4)),random.randint(0,255),random.randint(0,255))
    color_1 = QColor.fromHsv((hue + 60) % 360, 255, 255)
    
    gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
    gradient.setColorAt(0.0, color1)
    gradient.setColorAt(0.2, color2)
    gradient.setColorAt(0.4, color3)
    gradient.setColorAt(0.6, color4)
    gradient.setColorAt(0.8, color5)
    gradient.setColorAt(1.0, color_1)
    return gradient


# I HAD TO SEARCH FOR THIS IDEA
class CentralWidget(QWidget):
    ''' The central Widget had to be custom for the second waveform'''
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.main_window.is_talking:
            button_rect = self.main_window.push_to_talk_btn.geometry()
            button_center = button_rect.center()
            button_radius = button_rect.width() // 2
            wave_radius = button_radius
            if len(self.main_window.audio_data) < 360:
                return
            waveform = QPolygonF()
            for angle in range(360):
                theta = math.radians(angle)
                amplitude = self.main_window.audio_data[angle] * 200
                x = button_center.x() + (wave_radius + amplitude) * math.cos(theta)
                y = button_center.y() + (wave_radius + amplitude) * math.sin(theta)
                waveform.append(QPointF(round(x), round(y)))
            waveform.append(waveform[0])
            
            avg_amp = np.mean(np.abs(self.main_window.audio_data))
            
            grad_rect = QRectF(button_center.x() - (wave_radius + 200),
                               button_center.y() - (wave_radius + 200),
                               2 * (wave_radius + 200),
                               2 * (wave_radius + 200))
            gradient = create_dynamic_gradient(avg_amp, grad_rect)
            
            gradient.setColorAt(1.0, QColor(50, 0, 50))
            gradient.setColorAt(0.8, QColor(75, 0, 130))
            gradient.setColorAt(0.6, QColor(0, 0, 255))
            gradient.setColorAt(0.5, QColor(0, 128, 255))
            gradient.setColorAt(0.4, QColor(0, 255, 255))
            gradient.setColorAt(0.3, QColor(0, 255, 128))
            gradient.setColorAt(0.2, QColor(0, 255, 0))
            gradient.setColorAt(0.1, QColor(255, 255, 0))
            gradient.setColorAt(0.05, QColor(255, 128, 0))
            gradient.setColorAt(0.0, QColor(255, 0, 0))
            avg_amp = np.mean(np.abs(self.main_window.audio_data))
            thickness = max(2, int(avg_amp * 10))
            pen = QPen(QBrush(gradient), thickness)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPolyline(waveform)


class AudioCaptureThread(QThread):
    audio_data_signal = pyqtSignal(np.ndarray)  # Signal to send audio data

    def __init__(self, sample_rate=44100, chunk_size=1024):
        super().__init__()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.running = True
    def run(self):
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
                audio_chunk = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(audio_chunk, dtype=np.int16)

                normalized_data = audio_data / np.iinfo(np.int16).max

                self.audio_data_signal.emit(normalized_data)

            stream.stop_stream()
            stream.close()
            audio_interface.terminate()

        except:
            print(f"Error in audio thread.")

    def stop(self):
        self.running = False
        self.wait()


# UGLY BUT COOL
class ChatArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom)  # Align messages to the bottom because the opposite is buggy
        self.setLayout(self.layout)
        self.setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def add_user_message(self, message: str):
        label = QLabel(message)
        label.setWordWrap(True)
        label.setStyleSheet(
            "background-color: rgba(70,130,180,180); color: white; border-radius: 10px; padding: 8px;"
        )
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(label)
        self.scroll_to_bottom()  # Ensure scrolling to bottom after adding message

    def add_assistant_message(self, message: str):
        label = QLabel(message)
        label.setWordWrap(True)
        label.setStyleSheet(
            "background-color: rgba(105,105,105,180); color: white; border-radius: 10px; padding: 8px;"
        )
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(label)
        self.scroll_to_bottom()  # Ensure scrolling to bottom after adding message

    def scroll_to_bottom(self):
        parent_scroll_area = self.parentWidget()
        if isinstance(parent_scroll_area, QScrollArea):
            parent_scroll_area.verticalScrollBar().setValue(parent_scroll_area.verticalScrollBar().maximum())

# PATHETIC
class ChatScrollArea(QScrollArea):
    # Custom scroll because i suck
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self._auto_scroll = True
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

    def on_scroll(self, value):
        max_val = self.verticalScrollBar().maximum()
        self._auto_scroll = (max_val - value) < 50

    def scrollToBottomIfNeeded(self):
        QTimer.singleShot(0, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()))

# MUAHAUHAUHAUHAUHAUHAUHAUHA
class MainWindow(QMainWindow):
    spoke_signal = pyqtSignal(str)
    add_ass_message = pyqtSignal(str)
    req_fast_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.spoke_signal.connect(self.on_spoke)
        self.add_ass_message.connect(self.add_ass_msg)
        self.req_fast_signal.connect(self.request_fast)
        
        screen = QApplication.primaryScreen()
        size = screen.size()
        width = int(size.width() * 0.4)
        height = int(size.height() * 0.8)
        self.setMinimumSize(int(size.width() * 0.31), int(size.height() * 0.71))
        self.resize(width, height)
        self.setWindowTitle("SoreUI - OMEGAPyXero")
        self.setStyleSheet(f"background-color: {config()['General']['SecondaryColor']};color:{config()['General']['TextColor']};font-family:\"{config()['General']['Font']}\";")
        
        
        self.is_talking = False
        self.RequestEvent = xmanager.new(xmanager.Event)
        self.RequestEvent.connect(self.on_spoke)
        self.HandleMessage = xmanager.new(xmanager.Event)
        self.HandleMessage.connect(self.handle_chat_message)
        self.waveform_offset = 0
        self.wavefrom_amplitude = 20
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1)
        self.wave_amplitude = 5  # Height of waveform peaks
        self.num_points = 360  # Number of points in the circle
        self.frequency = 10  # Number of waveform oscillations
        self.audio_data = np.zeros(360)
        self.audio_thread = AudioCaptureThread()
        self.audio_thread.audio_data_signal.connect(self.update_audio_data)
        self.audio_thread.start()
        
        

        # Main layout and widgets
        central_widget = QWidget()
        central_widget = CentralWidget(main_window=self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # TOP BARR
        top_bar = QHBoxLayout()
        self.settings_button = QPushButton()
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.setIconSize(QSize(30,30))
        self.settings_button.setToolTip("Settings")
        self.settings_button.setIcon(QIcon(Path(__file__).joinpath('..').joinpath('data/settings.png').__str__()))  # Blank icon (set your own later)
        self.settings_button.setStyleSheet(self.getGlassButtonStyle())
        self.settings_button.clicked.connect(self.on_settings_clicked)
        top_bar.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignLeft)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        
        # Center AreEA
        center_layout = QVBoxLayout()
        center_layout.setSpacing(20)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Big black rounded "Push to talk" button
        self.push_to_talk_btn = QPushButton("Push to talk")
        self.push_to_talk_btn.setMinimumSize(200, 200)
        self.push_to_talk_btn.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.push_to_talk_btn.setStyleSheet(self.getBigButtonStyle())
        self.push_to_talk_btn.clicked.connect(self.on_push_to_talk)
        center_layout.addWidget(self.push_to_talk_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        # Add some space under push_to_talk_btn
        center_layout.addSpacing(20)
        # CHAT AREA
        self.chat_area_widget = ChatArea()
        self.chat_scroll = ChatScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setWidget(self.chat_area_widget)
        self.chat_scroll.setStyleSheet("background: transparent; border: none;")
        center_layout.addWidget(self.chat_scroll)
        main_layout.addLayout(center_layout)

        # TUCKS
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.switch_to_text_btn = QPushButton("Switch to text")
        self.switch_to_text_btn.setFixedHeight(40)
        self.switch_to_text_btn.setStyleSheet(self.getGlassButtonStyle())
        self.switch_to_text_btn.clicked.connect(self.on_switch_to_text)
        bottom_layout.addWidget(self.switch_to_text_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        # DROP SHADOW EFFECT
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 255, 255)) 
        shadow_effect.setOffset(0, 0)
        shadow_effect.setBlurRadius(155)
        self.push_to_talk_btn.setGraphicsEffect(shadow_effect)
        
        # AI SETUP
        self.messages = [get_system_command()]
        self.tools = tools.ALL_AVAILABLE_TOOLS
        self.is_processing = False
        self.last_3 = 3
        QShortcut(QKeySequence("Ctrl+D"),self,self.debug)
        ipu_timer = QTimer()
        ipu_timer.timeout.connect(self.is_process_update)
        ipu_timer.start(100)

    # TODO: This function literally has no purpose delete if possible
    def is_process_update(self):
        if self.is_processing:
            if self.last_3 > 0:
                self.last_3-=1
            else:
                self.last_3=3
            self.push_to_talk_btn.setText("Processing"+'.'*self.last_3)
    # YEAHHHHH GPT YEAEAHEAHEYAHEAHEA
    def getGlassButtonStyle(self) -> str:
        """Returns a QSS style for glass-like dark buttons."""
        return """
            QPushButton {
                background-color: """ + config()['General']['SecondaryColor'] + """;
                color: #fff;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 200);
            }
            QPushButton:pressed {
                background-color: rgba(30, 30, 30, 220);
            }
        """
    # getBigBlackButtonStyle
    def getBigButtonStyle(self) -> str:
        """Returns a QSS style for the big 'Push to talk' button."""
        return """
            QPushButton {
                background-color: rgba(80, 80, 80, 200);
                color: #fff;
                border: none;
                border-radius: 100px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: rgba(100, 100, 100, 230);
            }
            QPushButton:pressed {
                background-color: rgba(60, 60, 60, 250);
            }
        """
    # self.sett.remember is crazy
    def on_settings_clicked(self):
        self.setDisabled(True)
        self.sett = SettingsWindow(read_latest_config())
        self.sett.remember(self)
        self.sett.show()
    def debug(self):
        pass
    def on_switch_to_text(self):
        QMessageBox.warning(self,"Error","This section has some bugs.\nIn order to use text-based interface choose the web option instead.") # Im lying it's not done yet # Im still lying its done but I'm too lazy to sync them # Im not lying anymore
        # Never give up
    def add_ass_msg(self,text):
        self.add_chat_message(text,False)
        self.chat_scroll.scrollToBottomIfNeeded()
    def request_fast(self):
        if config()['API']['Platform'].lower() == 'multiplatform':
            api = xmanager.MultiPlatform(config()['API']['If']['MultiPlatform']['SelectedPlatforms'])
            self.HandleMessage.FireAll((api.random_request(self.messages,self.tools),))
        else:
            api = xmanager.SinglePlatform(config()['API']['If']['SinglePlatform'])
            self.HandleMessage.FireAll((api._request_assistant(self.messages,self.tools),))
    def on_spoke(self,text):
        random.seed = time.time()
        self.reset_push_to_talk()
        if text:
            self.add_chat_message(text)
            self.messages.append({'role':'user','content':text})
            self.request_fast()
        else:
            t2s = xmanager.Text2Speech(config()['Text2Speech'])
            t2s.speak("I didn't understand you.") # Realistically the speech2text sucks not that you spoke with a weird accent
    def wake_word(self):
        if self.is_talking:
            return
        else:
            if self.wake_flag:
                return
            self.wake_flag = True
            def _temp():self.wake_flag=False
            e = xmanager.new(xmanager.Event)
            e.connect(_temp)
            e.WaitFireAll(3000)
    def on_push_to_talk(self):
        if not self.is_talking:
            self.is_talking = True
            self.push_to_talk_btn.setText("Listening...")
            sp=xmanager.Speech2Text(config()['Speech2Text'])
            sp.listen(lambda text:self.spoke_signal.emit(text))
        else:
            self.reset_push_to_talk()
    def reset_push_to_talk(self):
        self.is_talking = False
        self.push_to_talk_btn.setText("Push to talk")
    def add_chat_message(self, message, from_user=True):
        if from_user:
            self.chat_area_widget.add_user_message(message)
        else:
            self.chat_area_widget.add_assistant_message(message)
        self.chat_scroll.scrollToBottomIfNeeded()
    def handle_chat_message(self,message):
        self.is_processing = True
        if type(message) == xmanager.MaxRetriesReached:
            t2s=xmanager.Text2Speech(config()['Text2Speech'])
            t2s.speak("Maximum Retries Reached, please relaunch the program.")
        try:
            message = message.dict()
        except:
            message = dict(message)

        if message['tool_calls']:
            for tool_call in message['tool_calls']:
                func_name = tool_call['function']['name']
                args = json.loads(tool_call['function']['arguments'])
                id = tool_call['id']
                resp=tools.call_func(func_name,args)
                # append the tool call itself
                for key in list(message.keys()):
                    if message[key] == None:
                        message.pop(key)
                self.messages.append(message)
                self.messages.append({'role':'tool','name':func_name,'content':json.dumps(resp),'tool_call_id':id})
            self.req_fast_signal.emit()
        else:
            for key in list(message.keys()):
                    if message[key] == None:
                        message.pop(key)
            self.messages.append(message)
            self.add_ass_message.emit(message['content'])
            t2s = xmanager.Text2Speech(config()['Text2Speech'])
            t2s.speak(message['content'])
        self.is_processing = False
    def update_audio_data(self, new_audio_data):
        # SOME NUMPY SHIT THAT IDK
        self.audio_data = np.interp(
            np.linspace(0, len(new_audio_data), 360),
            np.arange(len(new_audio_data)),
            new_audio_data
        )
    def draw_straight_waveform(self, painter:QPainter): #Draw a more noise-sensitive straight-line waveform
        # Get button geometry
        button_rect = self.push_to_talk_btn.geometry()
        button_center = button_rect.center()
        button_radius = button_rect.width() // 2
        wave_line_y = button_center.y() + button_radius + 30
        # GradientS
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
        
        average_amplitude = np.mean(np.abs(self.audio_data))
        line_thickness = max(2, int(average_amplitude * 10))
        painter.setPen(QPen(gradient, line_thickness)) 
        
        waveform = QPolygonF()

        # Calculate points for the waveform with increased noise sensitivity
        if self.is_talking:
            sensitivity_factor = 100  # Increase this factor for higher waves
        else:
            sensitivity_factor=0
        width = self.width()
        num_points = width 

        # Calculate points for the waveform
        for x in range(num_points):  # Loop through every pixel in the window width
            amplitude = self.audio_data[int(x % len(self.audio_data))] * sensitivity_factor  # Scaling
            y = wave_line_y + amplitude 
            waveform.append(QPointF(np.random.normal(x), y))

        # Draw the waveform line
        painter.drawPolyline(waveform)
    def paintEvent(self, event:QEvent): # Paint the animated waveform around the button.
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Set background image
        background_pixmap = QPixmap(str(Path(__file__).parent.joinpath("data/darkpurpleback.jpg")) if config()['General']['BackgroundImage'].lower()=='default' else config()['General']['BackgroundImage'])  # Replace with your image path
        if background_pixmap.isNull():
            painter.fillRect(self.rect(), QColor(50, 50, 50))
        else:
            painter.drawPixmap(self.rect(), background_pixmap)
        painter.drawPixmap(self.rect(), background_pixmap)
        
        if self.is_talking:
            # Get button geometry
            button_rect = self.push_to_talk_btn.geometry()
            button_center = button_rect.center()
            button_radius = button_rect.width() // 2
            wave_radius = button_radius  # Distance from the button
            if len(self.audio_data) < 360:
                return
            
            # Create the waveform path
            waveform = QPolygonF()
            for angle in range(360):
                theta = np.radians(angle)
                amplitude = self.audio_data[angle] * 200  # scaling
                x = button_center.x() + (wave_radius + amplitude) * np.cos(theta)
                y = button_center.y() + (wave_radius + amplitude) * np.sin(theta)
                waveform.append(QPointF(round(x), round(y)))

            # Ensure the waves path closes
            waveform.append(waveform[0])
            # Gradient
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

            # draw
            painter.drawPolyline(waveform)

            # Fill the area between the button and waveform 
            wave_fill = QPolygonF()
            wave_fill.append(QPointF(button_center.x(), button_center.y()))
            wave_fill += waveform
            wave_fill.append(QPointF(waveform[0].x(), waveform[0].y()))  
            painter.setBrush(QColor(255, 0, 0, 50))
            painter.setPen(Qt.PenStyle.NoPen) 
            painter.drawPolygon(wave_fill)
        self.draw_straight_waveform(painter)

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.audio_thread.stop()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    e=xmanager.new(xmanager.Event)
    e.connect(xmanager.start_listening_thread)
    e.WaitFireAll(5000,(window.wake_word,))
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
