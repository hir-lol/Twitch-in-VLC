import logging 
import pystray
import threading
from PIL import Image
from time import sleep
from typing import Callable
from tools import show_error, MainConfig
from .command import *

log = logging.getLogger(__name__)

class Tray ():
    def __init__(self,tab: Callable):
        log.debug("Иницилизация класса")
        self.image = Image.open(MainConfig.icon)
        self.q = MainConfig.q
        self.tabing = tab

        self.icon = pystray.Icon(
            "Twitch in VLC",
            self.image,
            "Twitch in VLC",
            menu = pystray.Menu(
                pystray.MenuItem("Tab",self.tab,default=True,visible=False)
            )
        )

    def tab(self):
        self.tabing()

    def _handler(self):
        comnd = {
            stream : self._stream,
            notify : self._notify,
            stop_stream : self._stop_stream
        }
        arg = []
        while True:
            while not self.q.empty():
                push = self.q.get()
                try:
                    comnd[push.get("type")](push)
                except KeyError:
                    arg.append(push)
            for item in arg:
                self.q.put(item)
            arg.clear()
            sleep(5.0)

    def _notify(self,arg:str|dict):
        match arg:
            case str():
                text = arg 
            case dict():
                text = arg.get("value")
        if self.icon.HAS_NOTIFICATION:
            log.info("Вывод уведомления")
            log.debug(f"Текст уведомления: {text}")
            self.icon.notify(text,"Twitch in VLC")
        else:
            log.info("Неудачная попытка вывода уведомления")

    def _stream(self,arg: dict):
        self._notify(f"{arg.get('value')} запустил стрим!")

    def _stop_stream(self,arg: dict):
        self._notify(f"{arg.get('value')} выключил стрим")

    def run(self):
        threading.Thread(target=self._run,daemon=True).start()

    def _run(self):
        log.info("Запуск трея")
        self.icon.run_detached()
        self._handler()