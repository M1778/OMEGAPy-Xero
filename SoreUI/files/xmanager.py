# I HADN'T IMPORTED THESE MANY LIBRARIES BEFORE IN MY LIFE LIKE WTF IS THIS
import pyaudio
import json
import random
import os
import pyttsx3
import numpy as np
import sounddevice as sd
import webrtcvad
import io
import wave
import threading
import difflib
import sys
try:
    from openwakeword.model import Model
    _HAS_OPENWAKEWORD = True
except ImportError:
    _HAS_OPENWAKEWORD = False
from omglib.tools import pathtools
from omglib.ai import tts,map
from omglib.llm import tools
from omglib.selector.selector import DictSelector
from omglib.llm import platforms
from omglib.ai import tts
from omglib.ai import map
from omglib.event import Event, new
from gtts import gTTS
from pathlib import Path
from threading import Thread

sys.excepthook = sys.__excepthook__

PublicEvent = new(Event)

P = lambda _:str(pathtools.smart_paths(__file__,'..',_).absolute())

OMEGAPYXERO_MODELS_PATH = str(Path(__file__).parent.parent.parent.joinpath("models").absolute())

if _HAS_OPENWAKEWORD:
    owwmodel = Model(wakeword_models=[P('data/omega_py.onnx')])
else:
    owwmodel = None
WAKEWORD_THRESHOLD = 0.5

config = None
TOOLS_ENABLED = True

def update_config(nconfig=None):
    global config
    if nconfig:
        config = nconfig
        return
    config=json.load(open(P('settings.json'),'r'))

class UnavailablePlatformError(BaseException):
    def __init__(self,msg):
        super().__init__(msg)
class MaxRetriesReached(BaseException):
    def __init__(self,msg):
        super().__init__(msg)

_S_DEF = ['API_KEY']
_S_CF  = ['API_KEY','ACCOUNT_ID']

def select_required(keys:list,plt_vars:dict):
    selector = DictSelector()
    selector.load_from_dict(plt_vars)
    selector_result = DictSelector()
    for key in keys:
        selector_result.add_selection(key,selector.select(key),True)
    return selector_result.select_all()

_AUTO_HANDLE = lambda x:select_required(_S_DEF,x)
_AUTO_HANDLE_CF = lambda x:select_required(_S_CF,x)

class SinglePlatform:
    def __init__(self,platform:dict):

        self.platform = None
        if platform['PlatformName'] == "OPENAI":
            self.set_platform(platforms.OpenAI,_AUTO_HANDLE(platform['PlatformVariables']))
        elif platform['PlatformName'] == "CLOUDFLARE":
            self.set_platform(platforms.CloudFlare,_AUTO_HANDLE_CF(platform['PlatformVariables']))
        elif platform['PlatformName'] == "GROQ":
            self.set_platform(platforms.Groq,_AUTO_HANDLE(platform['PlatformVariables']))
        elif platform['PlatformName'] == "TOGETHER":
            self.set_platform(platforms.TogetherAI,_AUTO_HANDLE(platform['PlatformVariables']))
        elif platform['PlatformName'] == "COHERE":
            self.set_platform(platforms.Cohere,_AUTO_HANDLE(platform['PlatformVariables']))
        elif platform['PlatformName'] == "MISTRAL":
            self.set_platform(platforms.Mistral,_AUTO_HANDLE(platform['PlatformVariables']))
        elif platform['PlatformName'] == "AVIANAI":
            self.set_platform(platforms.AvianAI,_AUTO_HANDLE(platform['PlatformVariables']))
        elif platform['PlatformName'] == "OPENROUTER":
            self.set_platform(platforms.OpenRouter,_AUTO_HANDLE(platform['PlatformVariables']))
        elif platform['PlatformName'] == "GEMINI":
            self.set_platform(platforms.Gemini,_AUTO_HANDLE(platform['PlatformVariables']))
        else:
            raise UnavailablePlatformError(f"The selected platform '{platform['PlatformName']}' is unavailable and not supported.")
    def set_platform(self,plt,vars):
        self.platform:platforms.OpenAI = plt(**{i[0].lower():i[1] for i in list(zip(list(vars.keys()),list(vars.values())))})
    def _request_assistant(self,messages:list,tools:dict=None):
        self.platform.messages = messages
        if TOOLS_ENABLED and tools and self.platform.tool_support:
            return self.platform.request(tools)
        else:
            return self.platform.request()

class MultiPlatform:
    def __init__(self,platforms_:list):
        self.platforms = []
        self.max_retries = 5
        self.retries = 0
        for plat in platforms_:
            self.platforms.append(SinglePlatform(plat))
    def smart_request(self,platform_index:int,messages:list,tools:dict=None):
        if self.retries >= self.max_retries:
            return MaxRetriesReached
        if tools:
            if TOOLS_ENABLED and self.platforms[platform_index].platform.tool_support:
                try:
                    return self.platforms[platform_index]._request_assistant(messages,tools)
                except:
                    self.retries+=1
                    return self.platforms[platform_index]._request_assistant(messages,tools)
            else:
                try:
                    return self.smart_request(platform_index=platform_index-1,messages=messages,tools=tools)
                except:
                    self.retries+=1
                    return self.smart_request(platform_index=platform_index-1,messages=messages,tools=tools)
        else:
            try:
                return self.platforms[platform_index]._request_assistant(messages)
            except:
                self.retries+=1
                return self.platforms[platform_index]._request_assistant(messages)
    def random_request(self,messages:list,tools:dict=None):
        return self.smart_request(random.randint(0,len(self.platforms)-1),messages,tools)
    def access(self,platform_index:int):
        return self.platforms[platform_index]
    def access_p(self,platform_index:int):
        return self.access(platform_index).platform

class SimpleTTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate",175)
        self.engine.setProperty("volume",1.0)
        self.engine.setProperty("voice",self.engine.getProperty("voices")[1].id)
    def speak(self,text,thread=False):
        if self.engine._inLoop:
            self.engine.endLoop()
        self.engine.stop()
        if thread:
            Thread(target=self.speak,args=(text,),daemon=True).start()
            return
        else:
            self.engine.say(text)
            self.engine.runAndWait()
class GoogleTTS:
    def __init__(self,language:str='en'):
        self.language = language
        self.is_speaking = False
    def speak(self,text,thread=False):
        if self.is_speaking:
            return
        if thread:
            Thread(target=self.speak,args=(text,),daemon=True).start()
            return
        else:
            self.is_speaking = True
            tts_ = gTTS(text=text,lang=self.language)
            tts_.save("temp.mp3")
            tts.play_mp3_bytes(open("temp.mp3","rb").read())
            try:
                os.remove("temp.mp3")
            except:...
            self.is_speaking = False
class MurfAI:
    def __init__(self,api_key:str,language:str='en-US-natalie'):
        self.client = tts.MurfAI(api_key)
        self.lang = language
        self.is_speaking = False
    def speak(self,text:str,thread=False):
        if self.is_speaking:
            return
        if thread:
            Thread(target=self.speak,args=(text,),daemon=True).start()
            return
        else:
            self.is_speaking = True
            try:
                self.client.speak(text,lang=self.lang,style='Conversation')
            except Exception as err:
                print("ERROR: ",err)
            self.is_speaking = False

class Playht:
    def __init__(self,userid:str,secretkey:str):
        self.client = tts.Playht(userid,secretkey)
        self.is_speaking = False
    def speak(self,text:str,thread=False):
        if self.is_speaking:
            return
        if thread:
            Thread(target=self.speak,args=(text,),daemon=True).start()
            return
        else:
            self.is_speaking = True
            try:
                self.client.speak(text)
            except:
                pass
            self.is_speaking = False

class Text2Speech:
    def __init__(self,platform:dict):
        self.platform = None
        if platform['Platform'] == "SIMPLETTS":
            self.platform = SimpleTTS()
        elif platform['Platform'] == "GTTS":
            self.platform = GoogleTTS()
        elif platform['Platform'] == "MURFAI":
            self.platform = MurfAI(**DictSelector().load_from_dict(select_required(['api_key'],{i[0].lower():i[1] for i in list(zip(list(platform['PlatformVariables'].keys()),list(platform['PlatformVariables'].values())))})).add_selection('language','en-US-natalie' if platform['Language'] == 'en' else platform['Language']).select_all())
        elif platform['Platform'] == "PLAYHT":
            self.platform = Playht(**DictSelector().load_from_dict(select_required(['userid','secretkey'],{i[0].lower():i[1] for i in list(zip(list(platform['PlatformVariables'].keys()),list(platform['PlatformVariables'].values())))})).select_all())
        else:
            raise ValueError(f"Invalid platform '{platform['Platform']}' specified for Text2Speech.")
    def speak(self,text:str,thread=True)->None:
        return self.platform.speak(text,thread)

class Vosk: 
    def __init__(self,language:str,msize:str):
        map.VMM.change_models_path(OMEGAPYXERO_MODELS_PATH)
        language = language if language in list(map.VoskModels.supported_languages.keys()) else map.Languages.English
        self.client = map.Vosk(language,msize if msize in map.VoskModels.GetAvailableSizes(language) else map.VoskModels.GetBestModel(language))
        self.client.init()
        self.model=self.client.get_model()
    def listen(self,func_=None):

        self.client.recognizer.SetWords(True)
        self.client.recognizer
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 4096  
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        output=''
        print("IN SPEAK MODE")
        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                if self.client.recognizer.AcceptWaveform(data):
                    result = json.loads(self.client.recognizer.Result())
                    output=result.get("text", "")
                    break

        except KeyboardInterrupt:
            print("\nStopped")

        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
        if func_ is not None:
            func_(output)
        return output
    def listen_thread(self,func_to_send_result):
        Thread(target=self.listen,args=(func_to_send_result,),daemon=True).start()
        return

class Whisper:
    def __init__(self,wmodel:str): 
        self.sample_rate = 16000  
        self.frame_duration = 30  
        self.vad = webrtcvad.Vad(3)  
        self.client= map.Whisper(wmodel if wmodel in map.WhisperModels.available_models else map.WhisperModels.Base)
        self.client.init()

    def record_until_silence(self):
        print("Speak now... (waiting for speech)")
        audio_buffer = []
        silence_timeout = 1.5  
        silent_chunks = 0
        max_silent_chunks = int(silence_timeout / (self.frame_duration / 1000))

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16,
            blocksize=int(self.sample_rate * self.frame_duration / 1000)
        ) as stream:
            while True:
                chunk, _ = stream.read(int(self.sample_rate * self.frame_duration / 1000))
                chunk = chunk.squeeze()  

                if self.vad.is_speech(chunk.tobytes(), self.sample_rate):
                    silent_chunks = 0
                    audio_buffer.append(chunk)
                else:
                    silent_chunks += 1
                    if silent_chunks > max_silent_chunks and len(audio_buffer) > 0:
                        break

        if len(audio_buffer) == 0:
            return np.array([], dtype=np.float32)

        audio_np = np.concatenate(audio_buffer).astype(np.float32) / 32768.0
        return audio_np
    def listen(self, func_=None):
        audio_data = self.record_until_silence()
        if audio_data.size == 0:
            if func_ is not None:
                func_("")
            return ""
        result = self.client.get_model().transcribe(audio_data, fp16=False)
        if func_ is not None:
            func_(result["text"].strip())
        return result["text"].strip()
    def listen_thread(self,func_to_send_result):
        Thread(target=self.listen,args=(func_to_send_result,),daemon=True).start()
        return
class Wit:
    def __init__(self,api_key:str,language:str='en'):
        self.client=map.Wit(api_key,language)
    def listen(self,func_=None):
        with map.Microphone() as source:
            map._R.adjust_for_ambient_noise(source,duration=1)
            try:
                audio = map._R.listen(
                    source, 
                    timeout=3,  
                    phrase_time_limit=60  
                )
            except map._SR.WaitTimeoutError:
                print("No speech detected.")
                return ""
        try:
            text = self.client.recognize(audio)
            if func_ is not None:
                func_(text)
            return text
        except map._SR.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except map._SR.RequestError:
            print("API unavailable.")
            return ""
    def listen_thread(self,func_to_send_result):
        Thread(target=self.listen,args=(func_to_send_result,),daemon=True).start()
        return

class VoskAPI:
    def __init__(self,language:str='en'):
        self.client=map.VoskAPI(language)
    def listen(self,func_=None):
        with map.Microphone() as source:
            map._R.adjust_for_ambient_noise(source,duration=1)
            try:
                audio = map._R.listen(
                    source, 
                    timeout=3,  
                    phrase_time_limit=60  
                )
            except map._SR.WaitTimeoutError:
                print("No speech detected.")
                return ""
        try:
            text = self.client.recognize(audio)
            if func_ is not None:
                func_(text)
            return text
        except map._SR.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except map._SR.RequestError:
            print("API unavailable.")
            return ""
    def listen_thread(self,func_to_send_result):
        Thread(target=self.listen,args=(func_to_send_result,),daemon=True).start()
        return

class GoogleAPI:
    def __init__(self,language:str='en'):
        self.client=map.Google(language)
    def listen(self,func_=None):
        with map.Microphone() as source:
            map._R.adjust_for_ambient_noise(source,duration=1)
            try:
                audio = map._R.listen(
                    source, 
                    timeout=3,  
                    phrase_time_limit=60  
                )
            except map._SR.WaitTimeoutError:
                print("No speech detected.")
                return ""
        try:
            text = self.client.recognize(audio)
            if func_ is not None:
                func_(text)
            return text
        except map._SR.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except map._SR.RequestError:
            print("API unavailable.")
            return ""
    def listen_thread(self,func_to_send_result):
        Thread(target=self.listen,args=(func_to_send_result,),daemon=True).start()
        return

class Sphinx:
    def __init__(self,language:str='en'):
        self.client=map.Sphinx(language)
    def listen(self,func_=None):
        with map.Microphone() as source:
            map._R.adjust_for_ambient_noise(source,duration=1)
            try:
                audio = map._R.listen(
                    source, 
                    timeout=3,  
                    phrase_time_limit=60  
                )
            except map._SR.WaitTimeoutError:
                print("No speech detected.")
                return ""
        try:
            text = self.client.recognize(audio)
            if func_ is not None:
                func_(text)
            return text
        except map._SR.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except map._SR.RequestError:
            print("API unavailable.")
            return ""
    def listen_thread(self,func_to_send_result):
        Thread(target=self.listen,args=(func_to_send_result,),daemon=True).start()
        return

class Cloudflare:
    def __init__(self,account_id:str,api_key:str):
        self.sample_rate = 16000  
        self.frame_duration = 30  
        self.vad = webrtcvad.Vad(3)  
        self.client=map.CloudFlare(account_id,api_key)
    def listen(self,func_=None):
        text=self.alternate_listen()
        if func_ is not None:
            func_(text)
        return text
    def record_until_silence(self):
        print("Speak now... (waiting for speech)")
        audio_buffer = []
        silence_timeout = 1.5  
        silent_chunks = 0
        max_silent_chunks = int(silence_timeout / (self.frame_duration / 1000))

        frames_per_chunk = int(self.sample_rate * self.frame_duration / 1000)

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16,
            blocksize=frames_per_chunk
        ) as stream:
            while True:
                chunk, _ = stream.read(frames_per_chunk)
                chunk = chunk.squeeze()  

                if self.vad.is_speech(chunk.tobytes(), self.sample_rate):
                    silent_chunks = 0
                    audio_buffer.append(chunk)
                else:
                    silent_chunks += 1
                    if silent_chunks > max_silent_chunks and len(audio_buffer) > 0:
                        break

        if len(audio_buffer) == 0:
            return []

        audio_int16 = np.concatenate(audio_buffer)

        with io.BytesIO() as wav_io:
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(1)          
                wav_file.setsampwidth(2)          
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            wav_bytes = wav_io.getvalue()

        audio_uint8 = list(wav_bytes)

        return audio_uint8
    def alternate_listen(self):
        audio = self.record_until_silence()
        resp = self.client.recognize(audio)
        if resp.status_code != 200:
            return ""
        return json.loads(resp.text)['result']['text']
    def listen_thread(self,func_to_send_result):
        Thread(target=self.listen,args=(func_to_send_result,),daemon=True).start()
        return

class Speech2Text:
    def __init__(self,platform:dict):
        self.platform = None
        if platform['Platform'] == "VOSK":
            self.platform = Vosk(platform['PlatformVariables']['Language'],platform['PlatformVariables']['MSize'])
        elif platform['Platform'] == "WHISPER":
            self.platform = Whisper(platform['PlatformVariables']['WModel'])
        elif platform['Platform'] == "WIT":
            self.platform = Wit(platform['PlatformVariables']['API_KEY'],platform['PlatformVariables']['Language'])
        elif platform['Platform'] == "GOOGLE":
            self.platform = GoogleAPI(platform['PlatformVariables']['Language'])
        elif platform['Platform'] == "VOSKAPI":
            print("Error: VoskAPI is broken, using google by default")
            self.platform = GoogleAPI(platform['PlatformVariables']['Language'])
        elif platform['Platform'] == "SPHINX":
            self.platform = Sphinx(platform['PlatformVariables']['Language'])
        elif platform['Platform'] == "CLOUDFLARE":
            self.platform = Cloudflare(platform['PlatformVariables']['ACCOUNT_ID'],platform['PlatformVariables']['API_KEY'])
        else:
            raise Exception("INVALID PLATFORM DETECTED")
    def listen(self,func_=None,thread=True):
        if thread:
            self.platform.listen_thread(func_)
        else:
            text = self.platform.listen(func_)
            if func_ is not None:
                func_(text)
            return text

def audio_callback(indata, frames, time, status):
    """Callback function called for each audio block captured by sounddevice."""
    if status:
        print("Audio status:", status)

    audio_block = indata[:, 0]

    audio_int16 = np.asarray(audio_block, dtype=np.int16)

    if owwmodel is None:
        return

    prediction = owwmodel.predict(audio_int16)

    for wake_word, score in prediction.items():
        if score > WAKEWORD_THRESHOLD:
            PublicEvent.FireAll()

def listen_for_wakeword():
    """Continuously listens to the microphone stream and calls the callback for each block."""
    samplerate = 16000      
    channels = 1            
    block_duration = 0.08   
    blocksize = int(samplerate * block_duration)  

    with sd.InputStream(samplerate=samplerate,
                        channels=channels,
                        dtype='int16',
                        blocksize=blocksize,
                        callback=audio_callback):

        threading.Event().wait()

def is_wake_word(recognized_text, threshold=0.8):
    WAKE_WORDS = ['hey omegapy','omegapy','omega']
    recognized_text = recognized_text.lower()
    for wake in WAKE_WORDS:

        if wake in recognized_text:
            return True

        ratio = difflib.SequenceMatcher(None, recognized_text, wake).ratio()
        if ratio >= threshold:
            return True
    return False
def listen_for_wake_word(e:Event):
    """
    Continuously listens to the microphone.
    When audio is captured, it uses Google's speech recognition to convert
    it to text, then checks for a wake word.
    """
    recognizer = map._R
    with map._SR.Microphone() as source:

        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:

                audio = recognizer.listen(source)
                try:

                    recognized_text = recognizer.recognize_google(audio)
                    if is_wake_word(recognized_text):
                        e.FireAll()

                except map._SR.UnknownValueError:
                    print("Audio was unintelligible")
                except map._SR.RequestError as e:
                    print("Could not request results from the recognition service; {0}".format(e))
            except Exception as e:
                print("An error occurred:", e)
def start_listening_thread(custom_func):
    """Starts the wake word listener in a daemon thread so that it runs continuously in the background."""

    PublicEvent.connect(custom_func)
    listener_thread = threading.Thread(target=listen_for_wakeword, daemon=True)
    listener_thread.start()

    return [PublicEvent] # DONEENOENAOSNEIAS EOIRANEO IASNEO NAIEN ASOEN OASEN FINNALLY