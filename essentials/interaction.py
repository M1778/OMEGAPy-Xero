import sys
import webbrowser
import subprocess
from pathlib import Path
from threading import Thread
from importlib import import_module
import os
import time
import random

# Cross-platform optional imports
try:
    from pydub import AudioSegment
    from pydub.playback import play as pydub_play
except ImportError:
    AudioSegment = None
    pydub_play = None

try:
    from playsound import playsound
except ImportError:
    playsound = None

try:
    from gtts import gTTS, lang as glang
except ImportError:
    gTTS = None
    glang = None

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

# Windows-only imports (conditional)
_IS_WINDOWS = sys.platform == "win32"

if _IS_WINDOWS:
    try:
        import windowsapps
    except ImportError:
        windowsapps = None
    try:
        import winapps
    except ImportError:
        winapps = None
    try:
        import win32ui
        import win32api
        import win32con
    except ImportError:
        win32ui = None
        win32api = None
        win32con = None
    try:
        import pyttsx3
    except ImportError:
        pyttsx3 = None
    try:
        import pyautogui as pyg
    except ImportError:
        pyg = None
else:
    windowsapps = None
    winapps = None
    win32ui = None
    win32api = None
    win32con = None
    pyttsx3 = None
    pyg = None

# TTS engine init (Windows pyttsx3 only)
_TTSengine = None
if pyttsx3 is not None:
    try:
        _TTSengine = pyttsx3.init()
        _TTSengine.setProperty('voice', _TTSengine.getProperty('voices')[1].id)
    except Exception:
        _TTSengine = None

_IS_SPEAKING = False

# GLOBAL VARIABLES
MESSAGEBOX_STYLE_ASK_YES_NO = 4
MESSAGEBOX_STYLE_ASK_OK_CANCEL = 1
MESSAGEBOX_STYLE_ERROR = 16
MESSAGEBOX_STYLE_QUESTION = 32
MESSAGEBOX_STYLE_INFO = 64


def convert_path(path: str):
    return str(Path(path).absolute())


def MessageBox(message: str, title: str, style: int = 0) -> str:
    if win32ui is None:
        raise OSError("MessageBox is only available on Windows with pywin32 installed.")
    _ = win32ui.MessageBox(message, title, style)
    if _ == 1:
        return "ok"
    elif _ == 2:
        return "cancel"
    elif _ == 6:
        return "yes"
    elif _ == 7:
        return "no"
    else:
        return _


def OpenApp(appname: str) -> bool:
    if not _IS_WINDOWS or windowsapps is None:
        return False
    try:
        windowsapps.open_app(appname)
        return True
    except Exception:
        return False


def ListInstalledAppsName() -> list:
    if not _IS_WINDOWS or winapps is None:
        return []
    output = []
    for app in list(winapps.list_installed()):
        output.append(app.name)
    return output


def UninstallApp(appname: str) -> bool:
    if not _IS_WINDOWS or winapps is None:
        return False
    if winapps.search_installed(appname) == []:
        return False
    ask = MessageBox(f"Do you really want to uninstall {appname}?", "AI Assistant", MESSAGEBOX_STYLE_ASK_YES_NO)
    if ask == "yes":
        winapps.uninstall(appname)
    return True


def OpenUrl(url: str):
    return webbrowser.open(url)


def SearchOnGoogle(keywords: str):
    keywords = keywords.replace(" ", "+")
    url = "https://www.google.com/search?q=" + keywords
    return webbrowser.open(url)


def OpenPath(path: str):
    if _IS_WINDOWS:
        return subprocess.Popen(["explorer.exe", convert_path(path)])
    else:
        return subprocess.Popen(["xdg-open", convert_path(path)])


def translate(text: str, from_: str, to: str):
    if GoogleTranslator is None:
        return text
    t = GoogleTranslator()
    return t.translate(text)


def _TextToSpeech(text: str, lang: str):
    global _IS_SPEAKING
    if gTTS is None:
        raise ImportError("gTTS is required for TextToSpeech. Install it with: pip install gTTS")
    if lang not in list(glang.tts_langs().keys()):
        text = translate(text, "auto", "en")
    if _IS_SPEAKING:
        while _IS_SPEAKING:
            time.sleep(0.1)

    tts = gTTS(text, lang=lang)
    os.makedirs("audio", exist_ok=True)
    f = f"audio/audio{random.randint(99999, 199999)}.mp3"
    tts.save(f)
    _IS_SPEAKING = True
    try:
        if AudioSegment is not None and pydub_play is not None:
            sound = AudioSegment.from_mp3(f)
            pydub_play(sound)
        elif playsound is not None:
            playsound(f)
        elif _TTSengine is not None:
            _TTSengine.say(text)
            _TTSengine.runAndWait()
        else:
            raise ImportError("No audio playback library available. Install pydub, playsound, or pyttsx3.")
    finally:
        _IS_SPEAKING = False
        try:
            os.remove(f)
        except OSError:
            pass


def TextToSpeech(text: str, lang: str = 'en'):
    _TextToSpeech(text, lang)


def import_lib(libname: str):
    return import_module(libname)
