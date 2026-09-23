from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtCharts import *
from omglib.tools.dicttools import perfectdict
from omglib.ai.tts import MurfAI,Playht,play_mp3_bytes
from omglib.ai import map as _map
from gtts import gTTS
from gtts.langs import _langs
from threading import Thread
from pathlib import Path
import psutil
import pyttsx3
import apiresource
import json
import sys
import time
import zipfile
import os
import shutil

def unzip_file(zip_path, extract_to):
    """
    Unzip a file to a specified directory.

    :param zip_path: Path to the zip file.
    :param extract_to: Directory to extract the files.
    """
    # Check if the file is a valid zip file
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"{zip_path} is not a valid zip file.")

    # Open the zip file and extract its contents
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        print(f"Extracting contents of {zip_path} to {extract_to}")
        zip_ref.extractall(extract_to)
        print("Extraction complete.")

_map.VMM.models_path=str(Path(__file__).parent.parent.parent.joinpath("models").absolute())


try:
    simpletts_engine = pyttsx3.init()
except Exception:
    simpletts_engine = None
#Predefined General Chat API TTS STT Security About Plugins

class SettingsWindow(QMainWindow):
    def __init__(self,config:dict):
        super().__init__()
        self.config = config
        self.setWindowTitle("Settings")
        self.setFixedSize(600,500)
        self.init_ui()
    def init_ui(self):
        # init
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        # General Config
        self.general_widget = QWidget()
        self.general = QVBoxLayout()
        self.general_widget.setLayout(self.general)
        self.add_general_widgets()

        # Chat Config
        self.chat_widget = QWidget()
        self.chat = QVBoxLayout()
        self.chat_widget.setLayout(self.chat)
        self.add_chat_widgets()
        
        # API Config
        self.api_widget = QWidget()
        self.api = QVBoxLayout()
        self.api_widget.setLayout(self.api)
        self.add_api_widgets()

        # Text2Speech Config
        self.tts_widget = QWidget()
        self.tts = QVBoxLayout()
        self.tts_widget.setLayout(self.tts)
        self.add_tts_widgets()

        # Speech2Text
        self.stt_widget = QWidget()
        self.stt = QVBoxLayout()
        self.stt_widget.setLayout(self.stt)
        self.add_stt_widgets()

        # Security
        self.sec_widget = QWidget()
        self.sec = QVBoxLayout()
        self.sec_widget.setLayout(self.sec)
        self.add_sec_widgets()

        # Plugins
        self.plugin_widget = QWidget()
        self.plugin = QVBoxLayout()
        self.plugin_widget.setLayout(self.plugin)
        self.add_plugin_widgets()

        # Tab config
        self.tab_widget.addTab(self.general_widget,"General")
        self.tab_widget.addTab(self.chat_widget,"Chat")
        self.tab_widget.addTab(self.api_widget,"API")
        self.tab_widget.addTab(self.tts_widget,"Text2Speech")
        self.tab_widget.addTab(self.stt_widget,"Speech2Text")
        self.tab_widget.addTab(self.sec_widget,"Security")
        self.tab_widget.addTab(self.plugin_widget,"Plugins")

        menubar=self.menuBar()
        file_menu = menubar.addMenu("File")
        save_settings = QAction("Save Settings",self)
        save_settings.triggered.connect(self.save_settings)
        file_menu.addAction(save_settings)
        load_settings = QAction("Load Settings...",self)
        load_settings.triggered.connect(self.load_new_settings)
        file_menu.addAction(load_settings)
        exit_settings = QAction("Exit",self)
        exit_settings.triggered.connect(self.close)
        file_menu.addAction(exit_settings)
    def remember(self,win:QMainWindow):
        self.win = win
    def refresh(self):
        self.clear_layout(self.general)
        self.clear_layout(self.chat)
        self.clear_layout(self.api)
        self.clear_layout(self.tts)
        self.clear_layout(self.stt)
        self.clear_layout(self.sec)
        self.clear_layout(self.plugin)
        self.add_general_widgets()
        self.add_chat_widgets()
        self.add_api_widgets()
        self.add_tts_widgets()
        self.add_stt_widgets()
        self.add_sec_widgets()
        self.add_plugin_widgets()
    def clear_layout(self, layout):
        """
        Helper function to clear all widgets in a given layout.
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
    def load_new_settings(self):
        f=QFileDialog.getOpenFileName(self,"Choose config file",filter="Config (*.json)")
        if f[0]:
            try:
                self.config_bk = self.config
                fp=open(f[0],'r')
                self.config=json.load(fp)
                fp.close()
                self.refresh()
            except Exception as err:
                self.config = self.config_bk
                self.refresh()
                QMessageBox.critical(self,"Settings","There was a critical error while loading the config.\nFailed to load the config please verify the config file and try again.")
        else:
            ...
    def save_button(self):
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_settings)
        return save_button
    def handle_text_change(self,widget:QLineEdit,section:str,variable:str):
        def _text_changed_event(text:str):
            self.config[section][variable] = text
        widget.textChanged.connect(_text_changed_event)
    def choose_file_handler_image_edition(self,btn_:QPushButton,on_:QLineEdit):
        def handle():
            new = QFileDialog.getOpenFileName(self,"Choose file",filter="Images (*.png *.jpg *.jpeg *.gif *.jfif *.webp)")
            on_.setText(new[0])
        btn_.clicked.connect(handle)
    def choose_file_handler(self,btn_:QPushButton,on_:QLineEdit):
        def handle():
            new = QFileDialog.getOpenFileName(self,"Choose file")
            on_.setText(new[0])
        btn_.clicked.connect(handle)
    
    def choose_color(self,btn_:QPushButton,section,variable):
        btn_.setStyleSheet(f"background-color:{self.config[section][variable]}")
        def handle():
            color = QColorDialog.getColor()
            if color.isValid():
                btn_.setStyleSheet(f"background-color:{color.name()}")
                self.config[section][variable]=color.name()
        
        btn_.clicked.connect(handle)
    def choose_font(self,fontcombo:QFontComboBox,section,variable):
        fontcombo.setCurrentFont(QFont(self.config[section][variable]))
        def handle(newfont):
            self.config[section][variable]=newfont.family()
        fontcombo.currentFontChanged.connect(handle)

    def add_general_widgets(self):
        self.background_image_label = QLabel("Background Image:")
        self.background_image_path = QLineEdit()
        self.background_image_path.setText(self.config['General']['BackgroundImage'])
        self.handle_text_change(self.background_image_path,'General','BackgroundImage')
        self.background_image_button = QPushButton("Choose File")
        self.choose_file_handler_image_edition(self.background_image_button,self.background_image_path)

        # Main Button Section
        self.main_button_bg_label = QLabel("Main Button Background Image:")
        self.main_button_bg_path = QLineEdit()
        self.main_button_bg_path.setText(self.config['General']['MainButtonBackgroundImage'])
        self.handle_text_change(self.main_button_bg_path,'General','MainButtonBackgroundImage')
        self.main_button_bg_button = QPushButton("Choose File")
        self.choose_file_handler_image_edition(self.main_button_bg_button,self.main_button_bg_path)

        # Primary Color
        self.general_primary_color_label = QLabel("Primary Color:")
        self.general_primary_color_button = QPushButton("Select Color")
        self.choose_color(self.general_primary_color_button,'General','PrimaryColor')

        # Secondary Color
        self.general_secondary_color_label = QLabel("Secondary Color:")
        self.general_secondary_color_button = QPushButton("Select Color")
        self.choose_color(self.general_secondary_color_button,'General','SecondaryColor')

        # Text color
        self.general_text_color_label = QLabel("Text Color:")
        self.general_text_color_button = QPushButton("Select Color")
        self.choose_color(self.general_text_color_button,'General','TextColor')

        # Font
        self.general_font_label = QLabel("Font:")
        self.general_font_button = QFontComboBox()
        self.choose_font(self.general_font_button,'General','Font')

        # Fixed Size Inputs
        self.fixed_size_label = QLabel("Fixed Size (Width x Height):")
        self.fixed_width = QSpinBox()  # Create QSpinBox for width
        self.fixed_width.setRange(0, 9999)  # Set range for width
        self.fixed_height = QSpinBox()  # Create QSpinBox for height
        self.fixed_height.setRange(0, 9999)  # Set range for height
        self.fixed_width.setValue(self.config['General']['WindowSize']['Width'])
        self.fixed_height.setValue(self.config['General']['WindowSize']['Height'])
        
        def _CUSTOM_FUNCTION_1(newValue):
            self.config['General']['WindowSize']['Width'] = newValue
        def _CUSTOM_FUNCTION_2(newValue):
            self.config['General']['WindowSize']['Height'] = newValue
        

        self.fixed_width.valueChanged.connect(_CUSTOM_FUNCTION_1)
        self.fixed_height.valueChanged.connect(_CUSTOM_FUNCTION_2)
        # Save Changes Button
        temp = QWidget()
        temp_ = QHBoxLayout()
        temp_.addWidget(self.background_image_path,5)
        temp_.addWidget(self.background_image_button,1)
        temp.setLayout(temp_)
        self.general.addWidget(self.background_image_label)
        self.general.addWidget(temp)
        # self.general.addWidget(self.background_image_path)
        # self.general.addWidget(self.background_image_button)
        
        temp = QWidget()
        temp_ = QHBoxLayout()
        temp_.addWidget(self.main_button_bg_path,5)
        temp_.addWidget(self.main_button_bg_button,1)
        temp.setLayout(temp_)

        self.general.addWidget(self.main_button_bg_label)
        self.general.addWidget(temp)
        self.general.addWidget(QLabel("Colors:"))
        temp = QWidget()
        temp_ = QHBoxLayout()
        temp_.addWidget(self.general_primary_color_label,0)
        temp_.addWidget(self.general_primary_color_button,1,alignment=Qt.AlignmentFlag.AlignLeft)
        temp_.addWidget(self.general_secondary_color_label,0)
        temp_.addWidget(self.general_secondary_color_button,1,alignment=Qt.AlignmentFlag.AlignLeft)
        temp_.addWidget(self.general_text_color_label,0)
        temp_.addWidget(self.general_text_color_button,1,alignment=Qt.AlignmentFlag.AlignLeft)
        temp.setLayout(temp_)
        self.general.addWidget(temp)

        self.general.addWidget(self.general_font_label)
        self.general.addWidget(self.general_font_button)
        
        
        temp = QWidget()
        temp_ = QHBoxLayout()
        self.general.addWidget(self.fixed_size_label)
        temp_.addWidget(QLabel("Width:"),0)
        temp_.addWidget(self.fixed_width,1,alignment=Qt.AlignmentFlag.AlignLeft)
        temp_.addWidget(QLabel("Height:"),0)
        temp_.addWidget(self.fixed_height,1,alignment=Qt.AlignmentFlag.AlignLeft)
        
        temp.setLayout(temp_)
        self.general.addWidget(temp)
        self.general.addWidget(self.save_button())

    def add_chat_widgets(self):
        # Primary Color
        self.chat_primary_color_label = QLabel("Primary Color:")
        self.chat_primary_color_button = QPushButton("Select Color")
        self.choose_color(self.chat_primary_color_button,'Chat','PrimaryColor')

        # Secondary Color
        self.chat_secondary_color_label = QLabel("Secondary Color:")
        self.chat_secondary_color_button = QPushButton("Select Color")
        self.choose_color(self.chat_secondary_color_button,'Chat','SecondaryColor')

        # Font
        self.chat_font_label = QLabel("Font:")
        self.chat_font_button = QFontComboBox()
        self.choose_font(self.chat_font_button,'Chat','Font')

        # Additional Css
        self.chat_additional_css_label = QLabel("Additional CSS:")
        self.chat_additional_css_input = QTextEdit()

        # ADD WIDGETS
        self.chat.addWidget(self.chat_primary_color_label)
        self.chat.addWidget(self.chat_primary_color_button)
        self.chat.addWidget(self.chat_secondary_color_label)
        self.chat.addWidget(self.chat_secondary_color_button)
        self.chat.addWidget(self.chat_font_label)
        self.chat.addWidget(self.chat_font_button)
        self.chat.addWidget(self.chat_additional_css_label)
        self.chat.addWidget(self.chat_additional_css_input)

        self.chat.addWidget(self.save_button())
    def add_api_widgets(self):
        self.api_label = QLabel("Select Platform:")
        self.api_dropdown = QComboBox()
        self.api_dropdown.addItems(["MultiPlatform","Open AI","Groq","Together AI","CloudFlare (Broken)","Avian AI","Cohere","Mistral","OpenRouter","Google Gemini"])

        self.api_platform = QStackedWidget() # HERE >.........................................................
        
        def check_platform_exist(exist):
            for i in self.config['API']['If']['MultiPlatform']['SelectedPlatforms']:
                        if i['PlatformName'].lower() == exist.lower():
                            return True
            return False
        def rcheck_platform_exist(exist):
            if check_platform_exist(exist):
                for i in self.config['API']['If']['MultiPlatform']['SelectedPlatforms']:
                    if i['PlatformName'].lower() == exist.lower():
                        self.config['API']['If']['MultiPlatform']['SelectedPlatforms'].remove(i)
                        return True
            return False

        # MultiPlatform
        def move_selected_item(item:QListWidgetItem):
            def special_task(platname:str,key:str):
                plat = apiresource.LoginAPIKey(platname)
                if plat.exec():
                    rcheck_platform_exist(key)
                    newlist.append({"PlatformName":key,"PlatformVariables":{"API_KEY":plat.api_key}})
                else:
                    QMessageBox.warning(self,"Settings","You did not login into the API, task failed successfully.")
                    return False
            
            newlist = self.config['API']['If']['MultiPlatform']['SelectedPlatforms']
            
            if item.text() == "Open AI":
                if special_task(item.text(),"OPENAI") == False:return
            elif item.text() == "Groq":
                if special_task(item.text(),"GROQ") == False:return
            elif item.text() == "Together AI":
                if special_task(item.text(),"TOGETHER") == False:return
            elif item.text() == "CloudFlare":
                cldflr = apiresource.LoginCloudFlare()
                if cldflr.exec():
                    rcheck_platform_exist("CLOUDFLARE")
                    newlist.append({"PlatformName":"CLOUDFLARE","PlatformVariables":{"ACCOUNT_ID":cldflr.account_id,"API_KEY":cldflr.api_key}})
                else:
                    QMessageBox.warning(self,"Settings","You did not login into the API, task failed successfully.")
                    return False
            elif item.text() == "Avian AI":
                if special_task(item.text(),"AVIANAI") == False:return
            elif item.text() == "Cohere":
                if special_task(item.text(),"COHERE") == False:return
            elif item.text() == "Mistral":
                if special_task(item.text(),"MISTRAL") == False:return
            elif item.text() == "OpenRouter":
                if special_task(item.text(),"OPENROUTER") == False:return
            elif item.text() == "Google Gemini":
                if special_task(item.text(),"GEMINI") == False:return
            else:
                QMessageBox.critical(self,"ERROR 0:BAD ARGUMENT",f"INVALID ARGUMENT ({item.text()}) DETECTED. PLEASE REINSTSALL OR RESTART THE PROGRAM")
                return
            self.config['API']['If']['MultiPlatform']['SelectedPlatforms'] = newlist
            self.api.multiplatform.platforms.takeItem(self.api.multiplatform.platforms.row(item))
            self.api.multiplatform.selected_platforms.addItem(item.text())
        def move_platform_item(item:QListWidgetItem):
            self.api.multiplatform.selected_platforms.takeItem(self.api.multiplatform.selected_platforms.row(item))
            self.api.multiplatform.platforms.addItem(item.text())
            if item.text() == "Open AI":
                rcheck_platform_exist("OPENAI")
            elif item.text() == "Groq":
                rcheck_platform_exist("GROQ")
            elif item.text() == "Together AI":
                rcheck_platform_exist("TOGETHER")
            elif item.text() == "CloudFlare":
                rcheck_platform_exist("CLOUDFLARE")
            elif item.text() == "Avian AI":
                rcheck_platform_exist("AVIANAI")
            elif item.text() == "Cohere":
                rcheck_platform_exist("COHERE")
            elif item.text() == "Mistral":
                rcheck_platform_exist("MISTRAL")
            elif item.text() == "OpenRouter":
                rcheck_platform_exist("OPENROUTER")
            elif item.text() == "Google Gemini":
                rcheck_platform_exist("GEMINI")
            else:
                QMessageBox.critical(self,"ERROR 0:BAD ARGUMENT",f"INVALID ARGUMENT ({item.text()}) DETECTED. PLEASE REINSTSALL OR RESTART THE PROGRAM")
                return
            
        
        self.api.multiplatform_widget = QWidget()
        self.api.multiplatform = QHBoxLayout()
        self.api.multiplatform_widget.setLayout(self.api.multiplatform)
        self.api.multiplatform.platforms = QListWidget()
        self.api.multiplatform.platforms.addItems(["Open AI","Groq","Together AI","CloudFlare","Avian AI","Cohere","Mistral","OpenRouter","Google Gemini (Recommended)"])
        self.api.multiplatform.platforms.itemDoubleClicked.connect(move_selected_item)
        
        self.api.multiplatform.selected_platforms = QListWidget()
        self.api.multiplatform.selected_platforms.itemDoubleClicked.connect(move_platform_item)

        def reset_lists():
            for platform_config in self.config["API"]["If"]["MultiPlatform"]["SelectedPlatforms"]:
                platform_name = platform_config["PlatformName"].lower()
                platform_item = self.map_platform_name(platform_name)
                if platform_item in ["Open AI","Groq","Together AI","CloudFlare","Avian AI","Cohere","Mistral","OpenRouter","Google Gemini (Recommended)"]:
                    self.api.multiplatform.selected_platforms.addItem(platform_item)
                    # Remove from the first list to avoid duplicates
                    items = self.api.multiplatform.platforms.findItems(platform_item, Qt.MatchFlag.MatchExactly)
                    if items:
                        self.api.multiplatform.platforms.takeItem(self.api.multiplatform.platforms.row(items[0]))
        reset_lists()
        
        self.api.multiplatform.addWidget(self.api.multiplatform.platforms)
        self.api.multiplatform.addWidget(self.api.multiplatform.selected_platforms)
        # Open AI
        def openai_singleplatform(apikey:str):
            if not apikey.strip():
                try:self.api.openai.bad_apikey
                except:
                    self.api.openai.bad_apikey = QLabel("Error: Invalid apikey, please provide a valid apikey")
                    self.api.openai.bad_apikey.setStyleSheet("color: red; font-size: 12px;")
                    self.api.openai.addWidget(self.api.openai.bad_apikey)
            else:
                try:
                    if self.api.openai.bad_apikey:
                        self.api.openai.bad_apikey.deleteLater()
                        del self.api.openai.bad_apikey
                except:
                    ...

            self.config['API']['If']['SinglePlatform']={"PlatformName":"OPENAI","PlatformVariables":{"API_KEY":apikey}}
        
        self.api.openai_widget = QWidget()
        self.api.openai = QVBoxLayout()
        self.api.openai_widget.setLayout(self.api.openai)
        self.api.openai.initialLabel = QLabel("Platform Selected: OpenAI")
        self.api.openai.apiinput_widget = QWidget()
        self.api.openai.apiinput = QHBoxLayout()
        self.api.openai.apiinput_widget.setLayout(self.api.openai.apiinput)
        self.api.openai.apikeyLabel = QLabel("API KEY: ")
        self.api.openai.apikeyInput = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "OPENAI" else "")
        self.api.openai.apikeyInput.textEdited.connect(openai_singleplatform)
        self.api.openai.addWidget(self.api.openai.initialLabel,0)
        self.api.openai.apiinput.addWidget(self.api.openai.apikeyLabel)
        self.api.openai.apiinput.addWidget(self.api.openai.apikeyInput)
        self.api.openai.addWidget(self.api.openai.apiinput_widget,1)
        # Groq
        def groq_singleplatform(apikey:str):
            if not apikey.strip():
                try:self.api.groq.bad_apikey
                except:
                    self.api.groq.bad_apikey = QLabel("Error: Invalid apikey, please provide a valid apikey")
                    self.api.groq.bad_apikey.setStyleSheet("color: red; font-size: 12px;")
                    self.api.groq.addWidget(self.api.groq.bad_apikey)
            else:
                try:
                    if self.api.groq.bad_apikey:
                        self.api.groq.bad_apikey.deleteLater()
                        del self.api.groq.bad_apikey
                except:
                    ...

            self.config['API']['If']['SinglePlatform']={"PlatformName":"GROQ","PlatformVariables":{"API_KEY":apikey}}
        
        self.api.groq_widget = QWidget()
        self.api.groq = QVBoxLayout()
        self.api.groq_widget.setLayout(self.api.groq)
        self.api.groq.initialLabel = QLabel("Platform Selected: Groq")
        self.api.groq.apiinput_widget = QWidget()
        self.api.groq.apiinput = QHBoxLayout()
        self.api.groq.apiinput_widget.setLayout(self.api.groq.apiinput)
        self.api.groq.apikeyLabel = QLabel("API KEY: ")
        self.api.groq.apikeyInput = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "GROQ" else "")
        self.api.groq.apikeyInput.textEdited.connect(groq_singleplatform)
        self.api.groq.addWidget(self.api.groq.initialLabel,0)
        self.api.groq.apiinput.addWidget(self.api.groq.apikeyLabel)
        self.api.groq.apiinput.addWidget(self.api.groq.apikeyInput)
        self.api.groq.addWidget(self.api.groq.apiinput_widget,1)
        
        # Together AI
        def together_singleplatform(apikey:str):
            if not apikey.strip():
                try:self.api.together.bad_apikey
                except:
                    self.api.together.bad_apikey = QLabel("Error: Invalid apikey, please provide a valid apikey")
                    self.api.together.bad_apikey.setStyleSheet("color: red; font-size: 12px;")
                    self.api.together.addWidget(self.api.together.bad_apikey)
            else:
                try:
                    if self.api.together.bad_apikey:
                        self.api.together.bad_apikey.deleteLater()
                        del self.api.together.bad_apikey
                except:
                    ...

            self.config['API']['If']['SinglePlatform']={"PlatformName":"TOGETHER","PlatformVariables":{"API_KEY":apikey}}
        
        self.api.together_widget = QWidget()
        self.api.together = QVBoxLayout()
        self.api.together_widget.setLayout(self.api.together)
        self.api.together.initialLabel = QLabel("Platform Selected: Together AI")
        self.api.together.apiinput_widget = QWidget()
        self.api.together.apiinput = QHBoxLayout()
        self.api.together.apiinput_widget.setLayout(self.api.together.apiinput)
        self.api.together.apikeyLabel = QLabel("API KEY: ")
        self.api.together.apikeyInput = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "TOGETHER" else "")
        self.api.together.apikeyInput.textEdited.connect(together_singleplatform)
        self.api.together.addWidget(self.api.together.initialLabel,0)
        self.api.together.apiinput.addWidget(self.api.together.apikeyLabel)
        self.api.together.apiinput.addWidget(self.api.together.apikeyInput)
        self.api.together.addWidget(self.api.together.apiinput_widget,1)
        
        # CloudFlare
        def cf_singleplatform(accountid:str):
            if not accountid.strip():
                try:self.api.cf.bad_apikey
                except:
                    self.api.cf.bad_apikey = QLabel("Error: Invalid apikey, please provide a valid apikey")
                    self.api.cf.bad_apikey.setStyleSheet("color: red; font-size: 12px;")
                    self.api.cf.addWidget(self.api.cf.bad_apikey)
            else:
                try:
                    if self.api.cf.bad_apikey:
                        self.api.cf.bad_apikey.deleteLater()
                        del self.api.cf.bad_apikey
                except:
                    ...
            self.config['API']['If']['SinglePlatform']['PlatformName'] = "CLOUDFLARE"
            self.config['API']['If']['SinglePlatform']['PlatformVariables']['ACCOUNT_ID']=accountid
            self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY']=self.api.cf.apikey2Input.text()
        self.api.cf_widget = QWidget()
        self.api.cf = QVBoxLayout()
        self.api.cf_widget.setLayout(self.api.cf)
        self.api.cf.initialLabel = QLabel("Platform Selected: CloudFlare")
        self.api.cf.apiinput_widget = QWidget()
        self.api.cf.apiinput = QHBoxLayout()
        self.api.cf.apiinput_widget.setLayout(self.api.cf.apiinput)
        self.api.cf.apikeyLabel = QLabel("Account ID:")
        self.api.cf.apikeyInput = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['ACCOUNT_ID'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "CLOUDFLARE" else "")
        self.api.cf.apikeyInput.textEdited.connect(cf_singleplatform)
        self.api.cf.addWidget(self.api.cf.initialLabel,0)
        self.api.cf.apiinput.addWidget(self.api.cf.apikeyLabel)
        self.api.cf.apiinput.addWidget(self.api.cf.apikeyInput)

        self.api.cf.apiinput2_widget = QWidget()
        self.api.cf.apiinput2 = QHBoxLayout()
        self.api.cf.apiinput2_widget.setLayout(self.api.cf.apiinput2)
        self.api.cf.apikey2Label = QLabel("API KEY:")
        self.api.cf.apikey2Input = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "CLOUDFLARE" else "")
        self.api.cf.apikey2Input.textEdited.connect(cf_singleplatform)
        self.api.cf.apiinput2.addWidget(self.api.cf.apikey2Label)
        self.api.cf.apiinput2.addWidget(self.api.cf.apikey2Input)
        

        self.api.cf.addWidget(self.api.cf.apiinput_widget,1)
        self.api.cf.addWidget(self.api.cf.apiinput2_widget,1)
        
        # Avian AI
        def avian_singleplatform(apikey:str):
            if not apikey.strip():
                try:self.api.avian.bad_apikey
                except:
                    self.api.avian.bad_apikey = QLabel("Error: Invalid apikey, please provide a valid apikey")
                    self.api.avian.bad_apikey.setStyleSheet("color: red; font-size: 12px;")
                    self.api.avian.addWidget(self.api.avian.bad_apikey)
            else:
                try:
                    if self.api.avian.bad_apikey:
                        self.api.avian.bad_apikey.deleteLater()
                        del self.api.avian.bad_apikey
                except:
                    ...

            self.config['API']['If']['SinglePlatform']={"PlatformName":"AVIANAI","PlatformVariables":{"API_KEY":apikey}}
        
        self.api.avian_widget = QWidget()
        self.api.avian = QVBoxLayout()
        self.api.avian_widget.setLayout(self.api.avian)
        self.api.avian.initialLabel = QLabel("Platform Selected: Avian AI")
        self.api.avian.apiinput_widget = QWidget()
        self.api.avian.apiinput = QHBoxLayout()
        self.api.avian.apiinput_widget.setLayout(self.api.avian.apiinput)
        self.api.avian.apikeyLabel = QLabel("API KEY: ")
        self.api.avian.apikeyInput = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "AVIANAI" else "")
        self.api.avian.apikeyInput.textEdited.connect(avian_singleplatform)
        self.api.avian.addWidget(self.api.avian.initialLabel,0)
        self.api.avian.apiinput.addWidget(self.api.avian.apikeyLabel)
        self.api.avian.apiinput.addWidget(self.api.avian.apikeyInput)
        self.api.avian.addWidget(self.api.avian.apiinput_widget,1)
        
        # Cohere
        def cohere_singleplatform(apikey:str):
            if not apikey.strip():
                try:self.api.cohere.bad_apikey
                except:
                    self.api.cohere.bad_apikey = QLabel("Error: Invalid apikey, please provide a valid apikey")
                    self.api.cohere.bad_apikey.setStyleSheet("color: red; font-size: 12px;")
                    self.api.cohere.addWidget(self.api.cohere.bad_apikey)
            else:
                try:
                    if self.api.cohere.bad_apikey:
                        self.api.cohere.bad_apikey.deleteLater()
                        del self.api.cohere.bad_apikey
                except:
                    ...

            self.config['API']['If']['SinglePlatform']={"PlatformName":"COHERE","PlatformVariables":{"API_KEY":apikey}}
        
        self.api.cohere_widget = QWidget()
        self.api.cohere = QVBoxLayout()
        self.api.cohere_widget.setLayout(self.api.cohere)
        self.api.cohere.initialLabel = QLabel("Platform Selected: Cohere AI")
        self.api.cohere.apiinput_widget = QWidget()
        self.api.cohere.apiinput = QHBoxLayout()
        self.api.cohere.apiinput_widget.setLayout(self.api.cohere.apiinput)
        self.api.cohere.apikeyLabel = QLabel("API KEY: ")
        self.api.cohere.apikeyInput = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "COHERE" else "")
        self.api.cohere.apikeyInput.textEdited.connect(cohere_singleplatform)
        self.api.cohere.addWidget(self.api.cohere.initialLabel,0)
        self.api.cohere.apiinput.addWidget(self.api.cohere.apikeyLabel)
        self.api.cohere.apiinput.addWidget(self.api.cohere.apikeyInput)
        self.api.cohere.addWidget(self.api.cohere.apiinput_widget,1)
        
        # Mistral
        def mistral_singleplatform(apikey:str):
            if not apikey.strip():
                try:self.api.mistral.bad_apikey
                except:
                    self.api.mistral.bad_apikey = QLabel("Error: Invalid apikey, please provide a valid apikey")
                    self.api.mistral.bad_apikey.setStyleSheet("color: red; font-size: 12px;")
                    self.api.mistral.addWidget(self.api.mistral.bad_apikey)
            else:
                try:
                    if self.api.mistral.bad_apikey:
                        self.api.mistral.bad_apikey.deleteLater()
                        del self.api.mistral.bad_apikey
                except:
                    ...

            self.config['API']['If']['SinglePlatform']={"PlatformName":"MISTRAL","PlatformVariables":{"API_KEY":apikey}}
        
        self.api.mistral_widget = QWidget()
        self.api.mistral = QVBoxLayout()
        self.api.mistral_widget.setLayout(self.api.mistral)
        self.api.mistral.initialLabel = QLabel("Platform Selected: Mistral AI")
        self.api.mistral.apiinput_widget = QWidget()
        self.api.mistral.apiinput = QHBoxLayout()
        self.api.mistral.apiinput_widget.setLayout(self.api.mistral.apiinput)
        self.api.mistral.apikeyLabel = QLabel("API KEY: ")
        self.api.mistral.apikeyInput = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "MISTRAL" else "")
        self.api.mistral.apikeyInput.textEdited.connect(mistral_singleplatform)
        self.api.mistral.addWidget(self.api.mistral.initialLabel,0)
        self.api.mistral.apiinput.addWidget(self.api.mistral.apikeyLabel)
        self.api.mistral.apiinput.addWidget(self.api.mistral.apikeyInput)
        self.api.mistral.addWidget(self.api.mistral.apiinput_widget,1)
        
        # Open Router
        def opr_singleplatform(apikey:str):
            if not apikey.strip():
                try:self.api.opr.bad_apikey
                except:
                    self.api.opr.bad_apikey = QLabel("Error: Invalid apikey, please provide a valid apikey")
                    self.api.opr.bad_apikey.setStyleSheet("color: red; font-size: 12px;")
                    self.api.opr.addWidget(self.api.opr.bad_apikey)
            else:
                try:
                    if self.api.opr.bad_apikey:
                        self.api.opr.bad_apikey.deleteLater()
                        del self.api.opr.bad_apikey
                except:
                    ...

            self.config['API']['If']['SinglePlatform']={"PlatformName":"OPENROUTER","PlatformVariables":{"API_KEY":apikey}}
        
        self.api.opr_widget = QWidget()
        self.api.opr = QVBoxLayout()
        self.api.opr_widget.setLayout(self.api.opr)
        self.api.opr.initialLabel = QLabel("Platform Selected: OpenRouter")
        self.api.opr.apiinput_widget = QWidget()
        self.api.opr.apiinput = QHBoxLayout()
        self.api.opr.apiinput_widget.setLayout(self.api.opr.apiinput)
        self.api.opr.apikeyLabel = QLabel("API KEY: ")
        self.api.opr.apikeyInput = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "OPENROUTER" else "")
        self.api.opr.apikeyInput.textEdited.connect(opr_singleplatform)
        self.api.opr.addWidget(self.api.opr.initialLabel,0)
        self.api.opr.apiinput.addWidget(self.api.opr.apikeyLabel)
        self.api.opr.apiinput.addWidget(self.api.opr.apikeyInput)
        self.api.opr.addWidget(self.api.opr.apiinput_widget,1)
        
        # Gemini
        def gemini_singleplatform(apikey:str):
            if not apikey.strip():
                try:self.api.gemini.bad_apikey
                except:
                    self.api.gemini.bad_apikey = QLabel("Error: Invalid apikey, please provide a valid apikey")
                    self.api.gemini.bad_apikey.setStyleSheet("color: red; font-size: 12px;")
                    self.api.gemini.addWidget(self.api.gemini.bad_apikey)
            else:
                try:
                    if self.api.gemini.bad_apikey:
                        self.api.gemini.bad_apikey.deleteLater()
                        del self.api.gemini.bad_apikey
                except:
                    ...

            self.config['API']['If']['SinglePlatform']={"PlatformName":"GEMINI","PlatformVariables":{"API_KEY":apikey}}
        
        self.api.gemini_widget = QWidget()
        self.api.gemini = QVBoxLayout()
        self.api.gemini_widget.setLayout(self.api.gemini)
        self.api.gemini.initialLabel = QLabel("Platform Selected: Google Gemini")
        self.api.gemini.apiinput_widget = QWidget()
        self.api.gemini.apiinput = QHBoxLayout()
        self.api.gemini.apiinput_widget.setLayout(self.api.gemini.apiinput)
        self.api.gemini.apikeyLabel = QLabel("API KEY: ")
        self.api.gemini.apikeyInput = QLineEdit(self.config['API']['If']['SinglePlatform']['PlatformVariables']['API_KEY'] if self.config['API']['If']['SinglePlatform']['PlatformName'] == "GEMINI" else "")
        self.api.gemini.apikeyInput.textEdited.connect(gemini_singleplatform)
        self.api.gemini.addWidget(self.api.gemini.initialLabel,0)
        self.api.gemini.apiinput.addWidget(self.api.gemini.apikeyLabel)
        self.api.gemini.apiinput.addWidget(self.api.gemini.apikeyInput)
        self.api.gemini.addWidget(self.api.gemini.apiinput_widget,1)
        

        self.api_platform.addWidget(self.api.multiplatform_widget)
        self.api_platform.addWidget(self.api.openai_widget)
        self.api_platform.addWidget(self.api.groq_widget)
        self.api_platform.addWidget(self.api.together_widget)
        self.api_platform.addWidget(self.api.cf_widget)
        self.api_platform.addWidget(self.api.avian_widget)
        self.api_platform.addWidget(self.api.cohere_widget)
        self.api_platform.addWidget(self.api.mistral_widget)
        self.api_platform.addWidget(self.api.opr_widget)
        self.api_platform.addWidget(self.api.gemini_widget)
        
        
        
        def update(index):
            _l = ["OPENAI","GROQ","TOGETHER","CLOUDFLARE","AVIANAI","COHERE","MISTRAL","OPENROUTER","GEMINI"]
            self.api_platform.setCurrentIndex(index)
            if index == 0:
                self.config['API']['Platform'] = "MultiPlatform"
            else:
                self.config['API']['Platform'] = "SinglePlatform"
            
            self.config['API']['If']['SinglePlatform']['PlatformName'] = _l[index-1]

        if self.config['API']['Platform']=='SinglePlatform':
            _l = ["OPENAI","GROQ","TOGETHER","CLOUDFLARE","AVIANAI","COHERE","MISTRAL","OPENROUTER","GEMINI"]
            self.api_platform.setCurrentIndex(_l.index(self.config['API']['If']['SinglePlatform']['PlatformName'])+1)
            self.api_dropdown.setCurrentIndex(_l.index(self.config['API']['If']['SinglePlatform']['PlatformName'])+1)
            
            

        self.api_dropdown.currentIndexChanged.connect(update)
        
        def api_role_command_activation(text:str):
            self.config['API']['RoleCommand']=text

        self.api_role_command = QComboBox()
        self.api_role_command.addItems(["BasicChatBot","Test1","Test2"])
        self.api_role_command.currentTextChanged.connect(api_role_command_activation)
        self.api_role_command.setCurrentText(self.config['API']['RoleCommand'])
        self.api_role_command.setMinimumSize(100,30)

        self.api.addWidget(self.api_label)
        self.api.addWidget(self.api_dropdown)
        self.api.addWidget(self.api_platform)
        self.api.addWidget(self.api_role_command)
        self.api.addWidget(self.save_button())
    def add_tts_widgets(self):
        self.tts_label = QLabel("Select Text2Speech API:")
        self.tts_dropdown = QComboBox()
        self.tts_dropdown.setMinimumHeight(30)
        self.tts_dropdown.addItems(["SimpleTTS (Local)","GoogleTTS (Recommended)","MurfAI","PlayHt (Best)"])
        
        self.tts_test_widget=QWidget()
        self.tts_test = QVBoxLayout()
        self.tts_test_widget.setLayout(self.tts_test)
        test_hbox_widget = QWidget()
        test_hbox = QHBoxLayout()
        test_hbox_widget.setLayout(test_hbox);self.tts_test_input = QTextEdit()
        test_hbox.addWidget(QLabel("Test Input Text:"),0,Qt.AlignmentFlag.AlignTop)
        test_hbox.addWidget(self.tts_test_input,1)
        self.tts_test_button = QPushButton("Test")
        hbox_widget = QWidget()
        hbox = QHBoxLayout()
        hbox_widget.setLayout(hbox)
        hbox.addWidget(QLabel())
        hbox.addWidget(self.tts_test_button)
        hbox.addWidget(QLabel())
        
        self.tts_test.addWidget(test_hbox_widget)
        self.tts_test.addWidget(hbox_widget)

        self.tts_stacked = QStackedWidget()
        
        self.tts.simpletts_widget = QWidget()
        self.tts.simpletts = QVBoxLayout()
        self.tts.simpletts_widget.setLayout(self.tts.simpletts)
        self.tts.simpletts.addWidget(QLabel("Selected TTS: SimpleTTS (Local)"))

        self.tts.gtts_widget = QWidget()
        self.tts.gtts = QVBoxLayout()
        self.tts.gtts_widget.setLayout(self.tts.gtts)
        self.tts.gtts.addWidget(QLabel("Selected TTS: GoogleTTS (API) [No apikey required]"))


        self.tts.murf_widget = QWidget()
        self.tts.murf = QVBoxLayout()
        self.tts.murf_widget.setLayout(self.tts.murf)
        self.tts.murf.addWidget(QLabel("Selected TTS: MurfAI (API)"))
        self.tts.murf.apikey_widget = QWidget()
        self.tts.murf.apikey = QHBoxLayout()
        self.tts.murf.apikey_widget.setLayout(self.tts.murf.apikey)
        self.tts.murf_apikey = QLineEdit()
        self.tts.murf.apikey.addWidget(QLabel("API Key: "),0)
        self.tts.murf.apikey.addWidget(self.tts.murf_apikey)
        self.tts.murf.addWidget(self.tts.murf.apikey_widget)


        self.tts.playht_widget = QWidget()
        self.tts.playht = QVBoxLayout()
        self.tts.playht_widget.setLayout(self.tts.playht)
        self.tts.playht.addWidget(QLabel("Selected TTS: PlayHT (API)"))

        self.tts.playht.userid_widget = QWidget()
        self.tts.playht.userid = QHBoxLayout()
        self.tts.playht.userid_widget.setLayout(self.tts.playht.userid)
        self.tts.playht_userid = QLineEdit()
        self.tts.playht.userid.addWidget(QLabel("UserID: "),0)
        self.tts.playht.userid.addWidget(self.tts.playht_userid)
        self.tts.playht.addWidget(self.tts.playht.userid_widget)

        self.tts.playht.sk_widget = QWidget()
        self.tts.playht.sk = QHBoxLayout()
        self.tts.playht.sk_widget.setLayout(self.tts.playht.sk)
        self.tts.playht_sk = QLineEdit()
        self.tts.playht.sk.addWidget(QLabel("Secret Key: "),0)
        self.tts.playht.sk.addWidget(self.tts.playht_sk)
        self.tts.playht.addWidget(self.tts.playht.sk_widget)

        self.tts_stacked.addWidget(self.tts.simpletts_widget)
        self.tts_stacked.addWidget(self.tts.gtts_widget)
        self.tts_stacked.addWidget(self.tts.murf_widget)
        self.tts_stacked.addWidget(self.tts.playht_widget)

        def update(index):
            if index == 0:self.config['Text2Speech']['Platform'] = "SIMPLETTS"
            elif index == 1:self.config['Text2Speech']['Platform'] = "GTTS"
            elif index == 2:self.config['Text2Speech']['Platform'] = "MURFAI"
            elif index == 3:self.config['Text2Speech']['Platform'] = "PLAYHT"
            else:
                QMessageBox.critical(self,"ERROR 0:BAD ARGUMENT",f"INVALID ARGUMENT INDEX ({index}) DETECTED. PLEASE REINSTSALL OR RESTART THE PROGRAM")
                return
            self.tts_stacked.setCurrentIndex(index)
            self.tts_stacked.currentWidget().layout().addWidget(self.tts_test_widget)

        self.tts_dropdown.currentIndexChanged.connect(update)

        _=self.config['Text2Speech']['Platform']
        if _ == "SIMPLETTS":
            self.tts_dropdown.setCurrentIndex(0)
            self.tts_stacked.currentWidget().layout().addWidget(self.tts_test_widget)
        elif _ == "GTTS":
            self.tts_dropdown.setCurrentIndex(1)
            self.tts_stacked.currentWidget().layout().addWidget(self.tts_test_widget)
        elif _ == "MURFAI":
            self.tts_dropdown.setCurrentIndex(2)
            self.tts_stacked.currentWidget().layout().addWidget(self.tts_test_widget)
            self.tts.murf_apikey.setText(self.config['Text2Speech']['PlatformVariables']['API_KEY'] if perfectdict.has_key(self.config['Text2Speech']['PlatformVariables'],'API_KEY') else "")
        elif _ == "PLAYHT":
            self.tts_dropdown.setCurrentIndex(3)
            self.tts_stacked.currentWidget().layout().addWidget(self.tts_test_widget)
            self.tts.playht_userid.setText(self.config['Text2Speech']['PlatformVariables']['USERID'] if perfectdict.has_key(self.config['Text2Speech']['PlatformVariables'],'USERID') else "")
            self.tts.playht_sk.setText(self.config['Text2Speech']['PlatformVariables']['SECRETKEY'] if perfectdict.has_key(self.config['Text2Speech']['PlatformVariables'],'SECRETKEY') else "")
        else:
            self.config['Text2Speech']['Platform'] = 'SIMPLETTS'
            update(0)

        def murf_event(text:str):
            self.config['Text2Speech']['PlatformVariables']['API_KEY'] = text
        self.tts.murf_apikey.textEdited.connect(murf_event)

        def playht_1(text:str):
            self.config['Text2Speech']['PlatformVariables']['USERID'] = text
        self.tts.playht_userid.textEdited.connect(playht_1)

        def playht_2(text:str):
            self.config['Text2Speech']['PlatformVariables']['SECRETKEY'] = text
        self.tts.playht_sk.textEdited.connect(playht_2)

        def Test_Speak():
            text = self.tts_test_input.toPlainText()
            _=self.config['Text2Speech']['Platform']
            lang = self.config['Text2Speech']['Language']
            if _ == "SIMPLETTS":
                if simpletts_engine is None:
                    QMessageBox.warning(self,"Settings","SimpleTTS is unavailable (eSpeak not installed).")
                    return
                if lang != 'en':
                    QMessageBox.warning(self,"Settings",f"SimpleTTS does not support the language (Only English): {_langs[lang]}")
                simpletts_engine.say(text)
                self.setDisabled(True)
                simpletts_engine.runAndWait()
                self.setEnabled(True)
            elif _ == "GTTS":
                gTTS(text=text,lang=lang).save("temp.mp3")
                fp=open("temp.mp3",'rb')
                mp3_data = fp.read()
                fp.close()
                play_mp3_bytes(mp3_data)
            elif _ == "MURFAI":
                if lang != 'en':
                    QMessageBox.warning(self,"Settings",f"MurfAI does not support the language (Only English): {_langs[lang]}")
                try:MurfAI(self.config['Text2Speech']['PlatformVariables']['API_KEY']).speak(text,style='Conversation')
                except Exception as err:QMessageBox.critical(self,"Settings",f"We have encountered an error while using the API :\n {err}")
            elif _ == "PLAYHT":
                try:Playht(self.config['Text2Speech']['PlatformVariables']['USERID'],self.config['Text2Speech']['PlatformVariables']['SECRETKEY']).speak(text)
                except Exception as err:QMessageBox.critical(self,"Settings",f"We have encountered an error while using the API :\n {err}")
            else:
                QMessageBox.critical(self,"ERROR 0:BAD ARGUMENT",f"INVALID ARGUMENT ({_}) DETECTED. PLEASE REINSTSALL OR RESTART THE PROGRAM")
                return
        
        self.tts_test_button.clicked.connect(Test_Speak)
        
        def change_lang(newlang:str):
            for i in range(len(_langs.values())):
                if list(_langs.values())[i] == newlang:
                    self.config['Text2Speech']['Language'] = list(_langs.keys())[i]
                    return
            QMessageBox.warning(self,"Settings","There was a critical error in the program, we will restore the language to English for you")
            self.config['Text2Speech']['Language'] = 'en'
            self.tts_language_list.setCurrentText("English")
        
        self.tts_language_widget = QWidget()
        self.tts_language = QHBoxLayout()
        self.tts_language_widget.setLayout(self.tts_language)
        self.tts_language.addWidget(QLabel("Langauge: "),0)
        self.tts_language_list = QComboBox()
        self.tts_language_list.addItems(list(_langs.values()))
        self.tts_language_list.setCurrentText("English")
        self.tts_language_list.setCurrentText(self.config['Text2Speech']['Language'])
        self.tts_language.addWidget(self.tts_language_list,1)
        self.tts_language_list.setMinimumHeight(30)
        self.tts_language_list.currentTextChanged.connect(change_lang)

        self.tts_test_input.setText("This is a test for my voice, my pride. This is the AI Ultimate challenge.")

        self.tts.addWidget(self.tts_label,0)
        self.tts.addWidget(self.tts_dropdown,1)
        self.tts.addWidget(self.tts_stacked,1)
        self.tts.addWidget(self.tts_language_widget)
        self.tts.addWidget(self.save_button())
    def add_stt_widgets(self):
        self.stt_label = QLabel("Selected Platform:")
        self.stt_combobox = QComboBox()
        self.stt_combobox.addItems(['Vosk (Local)','Whisper (Local)','Wit (API)','VoskAPI (API,BROKEN) [no apikey required]','Google (API) [no apikey required]<Recommended','Sphinx (API) [no apikey required]','CloudFlare (API)'])
        self.stt_1_widget = QWidget()
        self.stt_1_layout = QHBoxLayout()
        self.stt_1_widget.setLayout(self.stt_1_layout)
        self.stt_1_layout.addWidget(self.stt_label,0)
        self.stt_1_layout.addWidget(self.stt_combobox,1)
        
        self.stt_stacked = QStackedWidget()
        self.stt_present_widget = QWidget()
        self.stt_present = QVBoxLayout()
        self.stt_present_widget.setLayout(self.stt_present)

        self.stt.vosk_widget = QWidget()
        self.stt.vosk = QVBoxLayout()
        self.stt.vosk_widget.setLayout(self.stt.vosk)
        
        self.stt.vosk.language = QComboBox()
        langs_=[i for i in _map.Languages().__dir__() if i[0] !='_']
        langs_d={}
        langs_b={}
        for i in langs_:
            langs_d[getattr(_map.Languages,i)] = i
            langs_b[i] = getattr(_map.Languages,i)
        
        self.stt.vosk.language.addItems(langs_)
        self.stt.vosk.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],"English"))
        if not langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],False):
            self.config['Speech2Text']['PlatformVariables']['Language'] = langs_b['English']
        
        def language_change(changed_to:str):
            bk = self.config['Speech2Text']['PlatformVariables']['Language']
            self.config['Speech2Text']['PlatformVariables']['Language'] = langs_b[changed_to]
            self.stt.vosk.msize.clear()
            try:
                sizes = _map.VoskModels.GetAvailableSizes(self.config['Speech2Text']['PlatformVariables']['Language'])
            except KeyError:
                self.config['Speech2Text']['PlatformVariables']['Language'] = bk
                self.stt.vosk.language.setCurrentText(langs_d[bk])
                self.stt.vosk.msize.clear()
                try:
                    self.stt.vosk.msize.addItems(_map.VoskModels.GetAvailableSizes(self.config['Speech2Text']['PlatformVariables']['Language']))
                    QMessageBox.critical(self,"Settings",f"Sorry but Vosk doesn't support the following language : {langs_d[langs_b[changed_to]]}")
                    return
                except:
                    self.config['Speech2Text']['PlatformVariables']['Language'] = 'en'
                    self.stt.vosk.msize.addItems(_map.VoskModels.GetAvailableSizes(self.config['Speech2Text']['PlatformVariables']['Language']))
                    self.stt.vosk.language.setCurrentText("English")
                    return
            self.stt.vosk.msize.addItems(sizes)
            if _map.VMM.model_exists(_map.VoskModels.GetModel(self.config['Speech2Text']['PlatformVariables']['Language'],self.config['Speech2Text']['PlatformVariables']['MSize'].lower())):
                self.stt.vosk.mstatus_label.setText("Installed.")
                self.stt.vosk.mstatus_label.setStyleSheet("color:#90EE90")
            else:
                self.stt.vosk.mstatus_label.setText("Not Installed.")
                self.stt.vosk.mstatus_label.setStyleSheet("color:red")

        def msize_change(changed_to:str):
            if not changed_to:return
            self.config['Speech2Text']['PlatformVariables']['MSize'] = changed_to
            if _map.VMM.model_exists(_map.VoskModels.GetModel(self.config['Speech2Text']['PlatformVariables']['Language'],self.config['Speech2Text']['PlatformVariables']['MSize'].lower())):
                self.stt.vosk.mstatus_label.setText("Installed.")
                self.stt.vosk.mstatus_label.setStyleSheet("color:#90EE90")
            else:
                self.stt.vosk.mstatus_label.setText("Not Installed.")
                self.stt.vosk.mstatus_label.setStyleSheet("color:red")

        self.stt.vosk.language.currentTextChanged.connect(language_change)
        
        self.stt.vosk.msize = QComboBox()
        
        self.stt.vosk.language_widget = QWidget()
        self.stt.vosk.language_layout = QHBoxLayout()
        self.stt.vosk.language_widget.setLayout(self.stt.vosk.language_layout)
        self.stt.vosk.language_layout.addWidget(QLabel("Language: "),0)
        self.stt.vosk.language_layout.addWidget(self.stt.vosk.language,1)

        self.stt.vosk.msize_widget = QWidget()
        self.stt.vosk.msize_layout = QHBoxLayout()
        self.stt.vosk.msize_widget.setLayout(self.stt.vosk.msize_layout)
        self.stt.vosk.msize_layout.addWidget(QLabel("Model Size:"),0)
        self.stt.vosk.msize_layout.addWidget(self.stt.vosk.msize,1)

        self.stt.vosk.msize.addItems(_map.VoskModels.GetAvailableSizes(self.config['Speech2Text']['PlatformVariables']['Language']))
        
        self.stt.vosk.mstatus_widget = QWidget()
        self.stt.vosk.mstatus = QHBoxLayout()
        self.stt.vosk.mstatus_widget.setLayout(self.stt.vosk.mstatus)
        self.stt.vosk.mstatus.addWidget(QLabel("Model Status: "))
        self.stt.vosk.mstatus_label= QLabel("Installed." if _map.VMM.model_exists(_map.VoskModels.GetModel(self.config['Speech2Text']['PlatformVariables']['Language'],self.config['Speech2Text']['PlatformVariables']['MSize'].lower())) else "Not Installed.")
        self.stt.vosk.mstatus.addWidget(self.stt.vosk.mstatus_label,alignment=Qt.AlignmentFlag.AlignLeft)

        self.stt.vosk.install_btn = QPushButton("Download and Install")

        def download_task():
            model = _map.VoskModels.GetModel(self.config['Speech2Text']['PlatformVariables']['Language'],self.config['Speech2Text']['PlatformVariables']['MSize'].lower())
            if _map.VMM.model_exists(model):
                QMessageBox.critical(self,"Settings","The model is already installed.")
                self.stt.vosk.mstatus_label.setText("Already installed.")
                self.stt.vosk.mstatus_label.setStyleSheet("color:green")
                return
            if model:
                self.stt.vosk.mstatus_label.setText("Installing...")
                self.stt.vosk.mstatus_label.setStyleSheet("color:yellow")
                dialog=apiresource.WaitingDialog(f"Downloading {model['name']}...")
                def download_function(worker):
                    try:
                        _follow_download = _map.VMM.smart_download(model)
                    except SystemError as err:
                        QMessageBox.critical(self,"Settings",f"There was an critical error (probably because of omglib incompatibility)\nERROR MESSAGE:\n{err}")
                        return
                    _follow_download.start()
                    while True:
                        time.sleep(0.01)
                        worker.last_status = _follow_download.string_full_status()
                        if _follow_download.obj.isSuccessful():
                            print("BREAK IN FAS")
                            break
                        if worker.cancel_requested:
                            _follow_download.obj.pause()
                            _follow_download.obj.stop()
                            del _follow_download.obj
                            return
                    _follow_download.after_download()
                    _map.VMM.clear_cache(True)
                    worker.last_status = "Download Completed."
                    
                dialog.start_download(download_function)

                if dialog.exec() == QDialog.DialogCode.Rejected:
                    QMessageBox.critical(self,"Settings",f"Failed to download and install the model ({model['name']}).\n if you think this was a mistake try again.")
                    self.stt.vosk.mstatus_label.setText("Installation Failed.")
                    self.stt.vosk.mstatus_label.setStyleSheet("color:red")
                else:
                    if _map.VMM.model_exists(model):
                        QMessageBox.information(self,"Settings","Model downloaded successfully.")
                        self.stt.vosk.mstatus_label.setText("Installation Completed.")
                        self.stt.vosk.mstatus_label.setStyleSheet("color:green")
                    else:
                        QMessageBox.critical(self,"Settings",f"Failed to download and install the model ({model['name']}).\n if you think this was a mistake try again.")
                        self.stt.vosk.mstatus_label.setText("Installation Failed.")
                        self.stt.vosk.mstatus_label.setStyleSheet("color:red")
            

            else:
                QMessageBox.critical(self,"Settings","Couldn't Identify the model to download it, please try again.")
                return
        self.stt.vosk.install_btn.clicked.connect(download_task)

        self.stt.vosk.msize.currentTextChanged.connect(msize_change)



        self.stt.vosk.addWidget(self.stt.vosk.language_widget,1)
        self.stt.vosk.addWidget(self.stt.vosk.msize_widget,1)
        self.stt.vosk.addWidget(self.stt.vosk.mstatus_widget,1)
        self.stt.vosk.addWidget(self.stt.vosk.install_btn)

        

        # Whisper
        whisper_models = _map.WhisperModels.available_models
        self.stt.whisper_widget = QWidget()
        self.stt.whisper = QVBoxLayout()
        self.stt.whisper_widget.setLayout(self.stt.whisper)
        
        
        self.stt.whisper_model_widget = QWidget()
        self.stt.whisper_model = QHBoxLayout()
        self.stt.whisper_model_widget.setLayout(self.stt.whisper_model)

        self.stt.whisper_model_combobox = QComboBox()
        self.stt.whisper_model_combobox.addItems(whisper_models)

        self.stt.whisper_model.addWidget(QLabel("Whisper Model: "))
        self.stt.whisper_model.addWidget(self.stt.whisper_model_combobox,1)


        def whisper_model_change(ind):
            self.config['Speech2Text']['PlatformVariables']['WModel'] = whisper_models[ind]
        self.stt.whisper_model_combobox.currentIndexChanged.connect(whisper_model_change)
        
        self.stt.whisper_model_combobox.setCurrentText(self.config['Speech2Text']['PlatformVariables']['WModel'])

        self.stt.whisper.addWidget(self.stt.whisper_model_widget)

        self.stt.whisper_install = QPushButton("Check or Install")
        self.stt.whisper.addWidget(self.stt.whisper_install)


        def check_whisper():
            model=self.config['Speech2Text']['PlatformVariables']['WModel']
            _WModel = _map.Whisper(model)
            dialog = apiresource.WaitingDialog(f"Checking or Installing Model : \"{model}\"")
            dialog.message_box_title = "Whisper Checker"
            dialog.completion_message = "Successfuly checked and verified."
            dialog.cancel_message = "Checking operation got canceled."
            def check_whisper_(worker):
                t=Thread(target=_WModel.init)
                t.start()
                while not _WModel.get_model():
                    time.sleep(1)
                    worker.last_status = "Checking or Installing..."
                    if worker.cancel_requested:
                        worker.last_status = "Failed"
                        return
                worker.last_status = "Checked :>"
            
            dialog.start_download(check_whisper_)
            if dialog.exec() == QDialog.DialogCode.Rejected:
                QMessageBox.critical(self,"Settings","User canceled the operation.")
            else:
                if _WModel.get_model():
                    QMessageBox.information(self,"Settings","Model is verified and installed.")
                else:
                    QMessageBox.critical(self,"Settings","There was an error or interuption, please try again with good internet connection.")
        self.stt.whisper_install.clicked.connect(check_whisper)
        
        def combochk(index):
            self.stt_stacked.setCurrentIndex(index)
            if index == 0:
                self.config['Speech2Text']['Platform'] = "VOSK"
            elif index == 1:
                self.config['Speech2Text']['Platform'] = "WHISPER"
            elif index == 2:
                self.config['Speech2Text']['Platform'] = "WIT"
            elif index == 3:
                self.config['Speech2Text']['Platform'] = "VOSKAPI"
            elif index == 4:
                self.config['Speech2Text']['Platform'] = "GOOGLE"
            elif index == 5:
                self.config['Speech2Text']['Platform'] = "SPHINX"
            elif index == 6:
                self.config['Speech2Text']['Platform'] = "CLOUDFLARE"
            else:
                QMessageBox.critical(self,"Settings","Unknown Error: Cannot Identify selected Platform. Please reset the program.")

        self.stt_combobox.currentIndexChanged.connect(combochk)

        
        self.stt.wit_widget = QWidget()
        self.stt.wit = QVBoxLayout()
        self.stt.wit_widget.setLayout(self.stt.wit)

        self.stt.wit.api_widget = QWidget()
        self.stt.wit.api = QHBoxLayout()
        self.stt.wit.api_widget.setLayout(self.stt.wit.api)
        self.stt.wit.api.addWidget(QLabel("API KEY: "))
        self.stt.wit.api_input = QLineEdit(self.config['Speech2Text']['PlatformVariables']['API_KEY'])
        self.stt.wit.api.addWidget(self.stt.wit.api_input,1)

        self.stt.wit.addWidget(self.stt.wit.api_widget)

        def wit_api(changed:str):
            self.config['Speech2Text']['PlatformVariables']['API_KEY'] = changed
        
        self.stt.wit.api_input.textChanged.connect(wit_api)

        self.stt.wit.lang_widget = QWidget()
        self.stt.wit.lang = QHBoxLayout()
        self.stt.wit.lang_widget.setLayout(self.stt.wit.lang)
        self.stt.wit.lang.addWidget(QLabel("Language: "))
        self.stt.wit.language = QComboBox()
        self.stt.wit.lang.addWidget(self.stt.wit.language,1)
        self.stt.wit.addWidget(self.stt.wit.lang_widget)
        
        langs_=[i for i in _map.Languages().__dir__() if i[0] !='_']
        langs_d={}
        langs_b={}
        for i in langs_:
            langs_d[getattr(_map.Languages,i)] = i
            langs_b[i] = getattr(_map.Languages,i)
        
        self.stt.wit.language.addItems(langs_)
        self.stt.wit.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],"English"))

        def witlanguage_change(changed_to:str):
            self.config['Speech2Text']['PlatformVariables']['Language'] = langs_b[changed_to]

        self.stt.wit.language.currentTextChanged.connect(witlanguage_change)

        # VoskAPI
        self.stt.voskapi_widget = QWidget()
        self.stt.voskapi = QHBoxLayout()
        self.stt.voskapi_widget.setLayout(self.stt.voskapi)

        self.stt.voskapi.addWidget(QLabel("Language: "))
        self.stt.voskapi.language = QComboBox()
        self.stt.voskapi.addWidget(self.stt.voskapi.language,1)
        self.stt.voskapi.language.addItems(langs_)
        self.stt.voskapi.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],"English"))

        def voskapi_change(changed:str):
            self.config['Speech2Text']['PlatformVariables']['Language'] = langs_b[changed]
        self.stt.voskapi.language.currentTextChanged.connect(voskapi_change)

        # Google
        self.stt.google_widget = QWidget()
        self.stt.google = QHBoxLayout()
        self.stt.google_widget.setLayout(self.stt.google)

        self.stt.google.addWidget(QLabel("Language: "))
        self.stt.google.language = QComboBox()
        self.stt.google.addWidget(self.stt.google.language,1)
        self.stt.google.language.addItems(langs_)
        self.stt.google.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],"English"))

        self.stt.google.language.currentTextChanged.connect(voskapi_change)

        # Sphinx
        self.stt.sphinx_widget = QWidget()
        self.stt.sphinx = QHBoxLayout()
        self.stt.sphinx_widget.setLayout(self.stt.sphinx)

        self.stt.sphinx.addWidget(QLabel("Language: "))
        self.stt.sphinx.language = QComboBox()
        self.stt.sphinx.addWidget(self.stt.sphinx.language,1)
        self.stt.sphinx.language.addItems(langs_)
        self.stt.sphinx.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],"English"))

        self.stt.sphinx.language.currentTextChanged.connect(voskapi_change)

        # CloudFlare
        self.stt.cf_widget = QWidget()
        self.stt.cf = QVBoxLayout()
        self.stt.cf_widget.setLayout(self.stt.cf)

        self.stt.cf.hbox1_widget = QWidget()
        self.stt.cf.hbox1 = QHBoxLayout()
        self.stt.cf.hbox1_widget.setLayout(self.stt.cf.hbox1)

        self.stt.cf.hbox1.addWidget(QLabel("Account ID: "))
        self.stt.cf.account_id = QLineEdit(self.config['Speech2Text']['PlatformVariables']['ACCOUNT_ID'])
        self.stt.cf.hbox1.addWidget(self.stt.cf.account_id,1)
        self.stt.cf.addWidget(self.stt.cf.hbox1_widget)

        def accid_change(to:str):
            self.config['Speech2Text']['PlatformVariables']['ACCOUNT_ID']=to
        self.stt.cf.account_id.textChanged.connect(accid_change)

        self.stt.cf.hbox2_widget = QWidget()
        self.stt.cf.hbox2 = QHBoxLayout()
        self.stt.cf.hbox2_widget.setLayout(self.stt.cf.hbox2)

        self.stt.cf.hbox2.addWidget(QLabel("API KEY: "))
        self.stt.cf.api_key = QLineEdit(self.config['Speech2Text']['PlatformVariables']['API_KEY'])
        self.stt.cf.hbox2.addWidget(self.stt.cf.api_key,1)
        self.stt.cf.addWidget(self.stt.cf.hbox2_widget)

        def apikey_change(to:str):
            self.config['Speech2Text']['PlatformVariables']['API_KEY']=to
        self.stt.cf.api_key.textChanged.connect(apikey_change)

        


        self.stt_stacked.addWidget(self.stt.vosk_widget)
        self.stt_stacked.addWidget(self.stt.whisper_widget)
        self.stt_stacked.addWidget(self.stt.wit_widget)
        self.stt_stacked.addWidget(self.stt.voskapi_widget)
        self.stt_stacked.addWidget(self.stt.google_widget)
        self.stt_stacked.addWidget(self.stt.sphinx_widget)
        self.stt_stacked.addWidget(self.stt.cf_widget)


        def general_change(index):
            if index == 0:
                self.stt.vosk.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],"English"))
                if not langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],False):
                    self.config['Speech2Text']['PlatformVariables']['Language'] = langs_b['English']
            elif index == 2:
                self.stt.wit.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],'English'))
            elif index == 3:
                self.stt.voskapi.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],'English'))
            elif index == 4:
                self.stt.google.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],'English'))
            elif index == 5:
                self.stt.sphinx.language.setCurrentText(langs_d.get(self.config['Speech2Text']['PlatformVariables']['Language'],'English'))
        
        
        self.stt_combobox.currentIndexChanged.connect(general_change)

        _l = ["VOSK","WHISPER","WIT","VOSKAPI","GOOGLE","SPHINX","CLOUDFLARE"]
        self.stt_combobox.setCurrentIndex(_l.index(self.config['Speech2Text']['Platform']))
        self.stt_stacked.setCurrentIndex(self.stt_combobox.currentIndex())
        

        self.stt.addWidget(self.stt_1_widget,0)
        self.stt.addWidget(self.stt_stacked,1)
        self.stt.addWidget(self.save_button(),1) # If a model is not installed and settings are saved it will be installed automatically
    def add_sec_widgets(self):
        self.sec_enabled_widget = QWidget()
        self.sec_enabled = QHBoxLayout()
        self.sec_enabled_widget.setLayout(self.sec_enabled) 

        self.sec_enabled.addWidget(QLabel("Enabled: "),0)
        self.sec.enabled = QCheckBox("Security")
        self.sec_enabled.addWidget(self.sec.enabled,0)

        self.sec.enabled.setCheckState(Qt.CheckState.Checked if self.config['Security']['Enabled'] else Qt.CheckState.Unchecked)

        def set_disabled(*args:QWidget):
            for i in args:
                i.setDisabled(True)
        def set_enabled(*args:QWidget):
            for i in args:
                i.setEnabled(True)
        def setcheck(chk_option:int):
            if chk_option == 0:
                self.config['Security']['Enabled'] = False
                set_disabled(self.sec.method_widget,self.sec.input_password_widget)
            else:
                self.config['Security']['Enabled'] = True
                set_enabled(self.sec.method_widget,self.sec.input_password_widget)
        self.sec.enabled.stateChanged.connect(setcheck)

        self.sec.method_widget = QWidget()
        self.sec.method = QHBoxLayout()
        self.sec.method_widget.setLayout(self.sec.method)

        self.sec.method.addWidget(QLabel("Security method: "),0)
        self.sec.method.string = QLabel(self.config['Security']['SecurityMethod'])
        self.sec.method.addWidget(self.sec.method.string,1)

        self.sec.input_password_widget = QWidget()
        self.sec.input_password = QHBoxLayout()
        self.sec.input_password_widget.setLayout(self.sec.input_password)

        self.sec.input_password.addWidget(QLabel("Password: "),0)
        self.sec.input_password.password = QLineEdit(self.config['Security']['SecurityVariables']['InsecurePassword'])
        self.sec.input_password.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.sec.input_password.addWidget(self.sec.input_password.password,1)


        def update_password(text:str):
            self.config['Security']['SecurityVariables']['InsecurePassword'] = text
        self.sec.input_password.password.textChanged.connect(update_password)

        self.sec.input_password.show_password = QCheckBox("Show password")
        self.sec.input_password.show_password.setCheckState(Qt.CheckState.Unchecked)
        self.sec.input_password.addWidget(self.sec.input_password.show_password,0)

        def showpass(st):
            if st == 0:
                self.sec.input_password.password.setEchoMode(QLineEdit.EchoMode.Password)
            else:
                self.sec.input_password.password.setEchoMode(QLineEdit.EchoMode.Normal)
        self.sec.input_password.show_password.stateChanged.connect(showpass)




        setcheck(self.sec.enabled.checkState().value)
        showpass(self.sec.input_password.show_password.checkState().value)


        self.sec.addWidget(self.sec_enabled_widget)
        self.sec.addWidget(self.sec.method_widget)
        self.sec.addWidget(self.sec.input_password_widget)
        self.sec.addWidget(self.save_button())
    def add_plugin_widgets(self):
        self.plugin_list = QTableView()
        
        self.plugin.model = QStandardItemModel()
        self.plugin.model.setHorizontalHeaderLabels(["Plugin ID","Plugin Name","Plugin Path"])
        
        
        def update_data():
            # Clear the existing data in the model
            self.plugin.model.setRowCount(0)

            # Rebuild the data list
            self.plugin.data = []
            for ind, plugin in enumerate(self.config['Plugins']['InstalledPlugins']):
                self.plugin.data.append([ind, plugin['PluginName'], plugin['PluginFolderPath']])

            # Populate the model with new data
            for row in self.plugin.data:
                items = []
                for cell in row:
                    item = QStandardItem(str(cell))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make the item read-only
                    items.append(item)
                self.plugin.model.appendRow(items)

            # Set the updated model back to the view (if needed)
            self.plugin_list.setModel(self.plugin.model)

        update_data()

        self.plugin.selected_item = None

        def select_item(index):
            row = index.row()
            name = self.plugin.model.item(row,1).text()
            path = self.plugin.model.item(row,2).text()
            
            self.plugin.selected_item = [name,path]
            #print(f"Selected: {name} -- {path}")

        def find_index_by_name_and_path():
            if self.plugin.selected_item == None:return None
            l=self.config['Plugins']['InstalledPlugins']
            for i,x in enumerate(l):
                if self.plugin.selected_item[0] in x.values() and self.plugin.selected_item[1] in x.values():
                    return i
            return None
        
        self.plugin_list.clicked.connect(select_item)

        self.plugin_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        #self.plugin_list.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.plugin_list.verticalHeader().setVisible(False)

        self.plugin_buttons_widget = QWidget()
        self.plugin_buttons = QHBoxLayout()
        self.plugin_buttons_widget.setLayout(self.plugin_buttons)

        self.plugin.remove_plugin = QPushButton("Remove")
        self.plugin_buttons.addWidget(self.plugin.remove_plugin)
        self.plugin.restart_plugin = QPushButton("Refresh")
        self.plugin_buttons.addWidget(self.plugin.restart_plugin)
        self.plugin.install_plugin = QPushButton("Install")
        self.plugin_buttons.addWidget(self.plugin.install_plugin)

        def remove_event():
            if find_index_by_name_and_path() == None:
                QMessageBox.warning(self,"Settings","You haven't selected a plugin yet, click on the name of the plugin you want to select.")
                return
            ind=find_index_by_name_and_path()
            self.config['Plugins']['InstalledPlugins'].pop(ind)
            update_data()
        def restart():
            update_data()
            QMessageBox.information(self,"Settings","Refreshed.")
        def install_event():
            dialog = apiresource.PluginDialog()
            if dialog.exec() == QDialog.DialogCode.Accepted:
                plugin_name = dialog.plugin_name
                plugin_path = dialog.plugin_path
                plgs_path = str(Path(__file__).parent.joinpath("plugins").joinpath(plugin_name).absolute())
                try:
                    unzip_file(plugin_path,plgs_path)
                except Exception as err:
                    QMessageBox.critical(self,"Settings",f"Unexpected error: {err}")
                self.config['Plugins']['InstalledPlugins'].append({"PluginName":plugin_name,"PluginFolderPath":plgs_path,"PluginInstallScript":str(Path(plgs_path).joinpath("install.py")),"PluginActivateScript":str(Path(plgs_path).joinpath("run.py"))})
                update_data()
            else:
                QMessageBox.warning(self,"Settings","User might've canceled to install a new plugin.")

        self.plugin.remove_plugin.clicked.connect(remove_event)
        self.plugin.restart_plugin.clicked.connect(restart)
        self.plugin.install_plugin.clicked.connect(install_event)
        self.plugin.addWidget(self.plugin_list)
        self.plugin.addWidget(self.plugin_buttons_widget)
        self.plugin.addWidget(self.save_button())
        

    def map_platform_name(self, platform_name):
        """Map platform config names to display names."""
        mapping = {
            "openai": "Open AI",
            "groq": "Groq",
            "togetherai": "Together AI",
            "cloudflare": "CloudFlare",
            "avianai": "Avian AI",
            "cohere": "Cohere",
            "mistral": "Mistral",
            "openrouter": "OpenRouter",
            "gemini": "Google Gemini"
        }
        return mapping.get(platform_name, f"Unknown Object ({platform_name})")
    def save_settings(self):
        
        shutil.copyfile(str(Path(__file__).parent.joinpath("settings.json")),str(Path(__file__).parent.joinpath("backup_settings.json")))
        f=open(str(Path(__file__).parent.joinpath("settings.json")),'w')
        json.dump(self.config,f)
        f.close()
        QMessageBox.information(self,"Settings","Settings updated successfully.")
        QMessageBox.information(self,"Settings",str(self.config['Speech2Text']))
    def closeEvent(self, a0):
        #self.save_settings()
        try:
            if getattr(self,'win'):
                self.win.setEnabled(True)
                return a0.accept()
        except:
            del self
            psutil.Process(os.getpid()).terminate()
            return super().closeEvent(a0)

def read_latest_config()->dict:
    return json.load(open(str(Path(__file__).parent.joinpath("settings.json")),'r'))
if __name__ == "__main__":
    app = QApplication(sys.argv)
    config=json.load(open(str(Path(__file__).parent.joinpath("settings.json")),'r'))
    mainwindow = SettingsWindow(config)
    mainwindow.show()
    sys.exit(app.exec())
    