from tkinter import Tk, messagebox
import sys
import os
import json 
import customtkinter as ctk 
import queue
import storage
import threading
import subprocess
import ctypes 
import logging

log = logging.getLogger(__name__)
__all__ = ("load_config","get_base_path","show_error","MainConfig","tooltip","resorse_path")

def load_config(CONFIG_FILE):
    log.info(f"Чтение json файла по пути: {CONFIG_FILE}")
    if not os.path.exists(CONFIG_FILE):
        log.error("Не нашёлся файл для чтения")
        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.exception("Ошибка чтения config.json")
        return {}

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def resorse_path(relative_path):
    if hasattr(sys, "_MEINPASS"):
        return os.path.join(sys._MEINPASS , relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

_u32 = ctypes.windll.user32
_u32.MessageBoxW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
_u32.MessageBoxW.restype = ctypes.c_int

_MB_YESNO_Q = 0x24
_MB_OR_ERR = 0x10
_IDYES = 6

def show_error(title: str, message: str,tkinter: bool = False):
    if tkinter is True:
        root = Tk()
        root.withdraw() #Скрытие пустого окна
        messagebox.showerror(title, message)
        root.destroy()
    else:
        _u32.MessageBoxW(0,message,title,_MB_OR_ERR)

class Config():
    """
    Класс для общения информацией между другими классами
    """
    def __init__ (self,app = None):
        log.debug("Иницилизация класса")
        self.CONFIG_FILE = os.path.join(get_base_path()+"/scripts/config.json")
        self.icon = (get_base_path() + "/assets/ICON.ico")
                
        self.config = load_config(self.CONFIG_FILE)        

        self.q = queue.Queue()
        self.qapi = queue.Queue()
        self.api = storage.ApiWorker(self.qapi,self.q)
        self.api.start()
        self.app = app

    def save_config(self):
        log.info("Сохранение конфиг файла")
        try:
            with open(self.CONFIG_FILE, "w", encoding = "utf-8") as f:
                json.dump(self.config, f, indent=4,ensure_ascii=False)
        except Exception as e:
            show_error("Ошибка","Ошибка при сохранении конфига")
            log.exception("Ошибка при сохранении конфиг файла")

    def chek_queue (self, keys: str, callback):
        if self.app is None:
            log.error("Невозможно проверить очередь")
            return
        status = False
        line_queue = []
        while not self.q.empty():
            line = self.q.get()
            if not isinstance(line, dict):
                continue
            elif line.get("source") == keys:
                callback( line.get("value"))
                status = True
                break
            else:
                line_queue.append(line)
        for line in line_queue:
            self.q.put(line)
        if status is False:
            self.app.after(100,lambda: self.chek_queue(keys, callback))

    def get_available_qualities (self, twitch_url: str, mode: str):
        log.debug(f"Получение качеств у {twitch_url}")
        if mode == "module":
            threading.Thread(target=lambda: self.module(twitch_url),daemon=True).start()
        else:
            threading.Thread(target=lambda: self.portable(twitch_url),daemon=True).start()

    def module(self, twitch_url: str):
        from streamlink import Streamlink
        session = Streamlink()
        streams = session.streams(twitch_url)
        data = []
        for quality, stream in streams.items():
            data.append(quality)
        self.q.put( {
            "source": "kach",
            "value": data
        })
        return
    
    def portable(self, twitch_url: str):
        try:
            result = subprocess.run(
                ["streamlink", "--json", twitch_url],
                capture_output=True,
                text=True,
                check=True, creationflags = subprocess.CREATE_NO_WINDOW
            )
            data = json.loads(result.stdout)
            self.q.put( {
                "source": "kach",
                "value": list(data["streams"].keys())
            })
            return
        except subprocess.CalledProcessError as e:            
            log.exception("Streamlink выдал исключение при запросе качеств")
            error_text = (e.stderr or e.stdout or"").strip()
            if "No playable streams" in error_text:
                status = "offline"
            else:
                status = "error"
            self.q.put( {
                "source": "kach",
                "value": [status ,error_text]
            })
            return

MainConfig = Config()

class tooltip():
    """
    text - Текст подсказки
    app - Главное окно, то на чей основе будет создан обьект подсказки (дочерний виджет)
    bind - Обьект к которому будет привязываться подсказка
    """
    def __init__(self, text: str,app,bind=None):
        self.tooltip = ctk.CTkToplevel(app)
        self.tooltip.overrideredirect(True)
        self.tooltip.configure(bg="white")        
        self.tooltip.attributes("-transparentcolor","white")
        self.label = ctk.CTkLabel(self.tooltip,text=text,font=("Arial",12),corner_radius=8,fg_color="#2b2b2b")
        self.label.pack()
        self.tooltip.withdraw()
        if bind != None:
            bind.bind("<Enter>", self.on_enter)
            bind.bind("<Leave>", self.on_leave)
            self.bind = bind
    def edit_text(self, text: str):
        self.label.configure(text=text)
    def on_enter(self, event):
        self.tooltip.deiconify()
        self.tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")    
    def on_leave(self, event):
        self.tooltip.withdraw()
    def destroy(self):
        self.bind.unbind("<Enter>", funcid=None)
        self.bind.unbind("<Leave>", funcid=None)
        self.label.destroy()
        self.tooltip.destroy()
    def binds(self, widget = None):
        if widget is not None:
            self.bind = widget
        self.bind.bind("<Enter>", self.on_enter)
        self.bind.bind("<Leave>", self.on_leave)
    def unbinds(self):
        self.bind.unbind("<Enter>", funcid=None)
        self.bind.unbind("<Leave>", funcid=None)    