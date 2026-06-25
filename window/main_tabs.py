import subprocess
import threading
import customtkinter as ctk 
from PIL import Image
import shutil
from tools import *
import logging

log = logging.getLogger(__name__)

class tab_twitch():
    def __init__(self, app, window):
        log.debug("Создание окна")
        self.start_btn_text = "Start stream"
        self.stop_btn_text = "Stop stream"
        self.quality_box_text = "Подтвердите ник снова"
        self.start_btn = ctk.CTkButton(app, text=self.start_btn_text, command=lambda: self.active_strim_btn(), state = "disabled")
        self.start_btn.pack(pady=20)
        self.core_ready_tooltip = tooltip(text="Ядро ещё не запустилось",app=window,bind=self.start_btn)
        self.core_ready_tooltip.unbinds()

        self.stream_running = False
        self.chat_var = ctk.BooleanVar(value=True)

        self.url_entry = ctk.CTkEntry(app, placeholder_text="https://www.twitch.tv/...")
        self.url_entry.pack(pady=10)
        self.tooltip_url_entry = tooltip(text="Ведите никнейм канала",app=window,bind=self.url_entry)
        self.url_entry.bind("<Return>", lambda e:self.on_channel_confirm())

        self.quality_box = ctk.CTkComboBox(
            app,
            values=[],state = "disabled")
        self.quality_box.pack(pady=5)
        self.quality_box.configure(command=lambda _: self.check_ready())

        self.confirm_btn = ctk.CTkButton(
            app,
            text="Подтвердить ник",
            command=lambda:self.on_channel_confirm()
        )
        self.confirm_btn.pack(pady=5)

        self.chat_checkbox = ctk.CTkCheckBox(app, text = "Запускать ли чат?", variable = self.chat_var)
        self.chat_checkbox.pack(pady=5)

        self.reset_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/reset.png"), dark_image = Image.open(get_base_path()+"/assets/reset.png"), size = (20,20))
        self.reset_button = ctk.CTkButton(
            app,
            image = self.reset_image,
            width = 20,
            height = 20,
            text = "",
            hover=False,
            corner_radius=10,
            command=lambda:self.reset()
        )
        self.reset_button.place(relx = 0, rely = 0,anchor="nw", x = 5, y = 20)
        self.reset_tooltip = tooltip("Сбросить ведёные данные и разблокировать кнопки",window,self.reset_button)

        self.communicate = MainConfig
        self.app = window
        self.mode = "twitch"
        self.q = self.communicate.q
        self.config = self.communicate.config
        self.dop_config = self.config.get("More_Setting") if "More_Setting" in self.config else {}
        self.qualites_state = False

    def reset(self):
        log.info("Нажата кнопка сброса")
        if self.stream_running is True:
            if self.dop_config.get("Reset_close_mode") is True and self.core_ready is True:
                self.active_strim_btn(False)
            else:
                return
        elif self.qualites_state is True :
            log.debug("Очистка полученых данных")

            self.confirm_btn.configure(state="normal")
            self.quality_box.set("")
            self.quality_box.configure(values=[],state="disabled")
            self.url_entry.configure(state="normal")
            self.url_entry.delete(0, ctk.END)
            self.start_btn.configure(state="disabled")

            self.qualites_state = False
        if self.dop_config.get("Reset_mode") is True:
            self.url_entry.delete(0, ctk.END)

    def active_strim_btn(self,close: bool = True):
        log.debug("Нажата кнопка Start")
        if not self.stream_running:
            log.info("Запуск стрима")
            self.stream_running = True
            self.start_stream()
        else:
            log.info("Остановка стрима")
            if self.core_ready is False:
                show_error("Ошибка","Ядро ещё не запустилось для закрытия")
                log.warning("Ядро не готово к закрытию")
                return
            self.stop_stream(close)
            self.stream_running = False

    def stop_stream(self, close: bool = True):
        if self.core_error is False:
            if close is True:
                self.proc.stdin.write("exit\n")
                self.proc.stdin.flush()
            else: 
                self.proc.stdin.write("stop\n")
                self.proc.stdin.flush()

        self.start_btn.configure(text=self.start_btn_text,fg_color = "green", state = "disabled")
        
        self.quality_box.configure(state="normal")
        self.quality_box.set("")
        self.quality_box.configure(values=[])
        if close is True:
            self.quality_box.set(self.quality_box_text)
        self.quality_box.configure(state = "disabled")
        
        self.url_entry.configure(state="normal")
        self.chat_checkbox.configure(state="normal")
        self.confirm_btn.configure(state="normal")
        self.reset_button.configure(state="normal")

        self.qualites_state = False

    def start_stream(self):
        self.on_start()
        self.core_ready = False
        self.core_ready_tooltip.binds()
        threading.Thread(target=self.read_stdout,daemon=True).start()            
        self.app.after(100,self.check_core_ready)
        
        self.start_btn.configure(text=self.stop_btn_text,fg_color = "red")            
        self.quality_box.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.chat_checkbox.configure(state="disabled")
        self.confirm_btn.configure(state="disabled")
        if self.dop_config.get("Reset_close_mode") is not True:
            self.reset_button.configure(state="disabled")

    def check_core_ready(self):
        queues = []
        while not self.q.empty():
            line = self.q.get()
            if not isinstance(line, dict):
                continue
            elif line.get("source") == "core":
                line = line.get("value")
                if line and line == "PROCESS_CLOSED" and self.proc.poll() != None:
                    log.warning("Ядро закрылось раньше чем ожидалось")
                    self.core_ready = True
                    self.core_error = True
                    self.active_strim_btn()
                    self.core_ready_tooltip.unbinds()
                    show_error("Ой","Кажется ядро закрылось раньше чем ожидалось")
                    return
                if line and "ready" in line:
                    log.info("Ядрл готово к закрытию")
                    self.core_ready = True
                    self.core_error = False
                    self.core_ready_tooltip.unbinds()
                    return
            else:
                queues.append(line)                    
        for line in queues:
            self.q.put(line)
        self.app.after(100,self.check_core_ready)

    def read_stdout(self):
        if self.proc.poll() != None:
            self.q.put({
                "source": "core",
                "value":"PROCESS_CLOSED"
            })
        while self.proc.poll() is None:
            line = self.proc.stdout.readline()
            if line:
                self.q.put({
                    "source": "core",
                    "value": str(line.strip())
                })       
        self.q.put({
            "source": "core",
            "value":"PROCESS_CLOSED"
        })    

    def on_start(self):
        channel = self.url_entry.get().strip()
        quality = self.quality_box.get().strip()
        open_chat = self.chat_var.get()
        
        if self.mode == "twitch":
            self.config["mode"] = [(self.config["mode"])[0],self.mode]
            self.config["channel"] = channel
            self.config["kach"] = quality
            self.config["otv"] = bool(open_chat)
        else:
            url = "https://" + channel
            self.config["mode"] = [(self.config["mode"])[0],self.mode]
            self.config["URL"] = url
            self.config["URL_KACH"] = quality
            
        MainConfig.save_config()
        core_pat = str(get_base_path() + "/scripts/core.exe")
        self.proc = subprocess.Popen([core_pat], shell= False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)

    def check_ready(self):
        channel_ok = bool(self.url_entry.get().strip())
        quality_ok = bool(self.quality_box.get().strip())

        if channel_ok and quality_ok:
            self.start_btn.configure(state="normal")
            self.start_btn.configure(fg_color = "green")
        else:
            self.start_btn.configure(state="disabled")

    def on_channel_confirm(self):
        log.info("Запрос качеств")
        if (self.config.get("mode"))[0] =="portable":
            if not shutil.which("streamlink"):
                log.error("Streamlink не найден")
                show_error("Streamlink не найден","Streamlink не обнаружен в PATH\nУстановите Streamlink и перезапустите программу")
                return
        
        if self.mode == "twitch":
            channel = self.url_entry.get().strip().lower()
        else:
            channel = self.url_entry.get().strip()

        if not channel:
            log.warning("Попытка запроса качеств при ведёном пустом поле")
            show_error("Ошибка названия", "Введите никнейм/название а не пустое поле")
            return

        if self.mode == "twitch":
            twitch_url = f"https://www.twitch.tv/{channel}"
        else:
            twitch_url = f"https://{channel}"

        self.quality_box.configure(state = "normal")
        self.quality_box.set("Получение")
        self.quality_box.configure(state = "disabled")
        self.confirm_btn.configure(state="disabled")
        self.url_entry.configure(state = "disabled")
        self.communicate.get_available_qualities(twitch_url,(self.config.get("mode"))[0])
        self.communicate.chek_queue("kach", self.edit_qualities)

    def edit_qualities(self, qualities: list):
        log.info("Получены качества")
        if not qualities or qualities[0] == "offline" or qualities[0] == "error":
            log.warning("Полученные качества содержут ошибку")
            if not qualities:
                pass
            else:
                log.warning(qualities[1])
            show_error("Ошибка проверки доступных качеств", "Не удалось получить настройки качества, возможно эфир офлайн.\n Или видён некоректный никнейм/название")
            self.quality_box.configure(state = "normal")
            self.quality_box.set("")
            self.quality_box.configure(state = "disabled")      
            self.confirm_btn.configure(state="normal")      
            self.url_entry.configure(state = "normal")
            self.qualites_state = False
            return

        self.qualites_state = True
        self.quality_box.configure(values=qualities)
        self.quality_box.configure(state = "readonly")
        self.quality_box.set("")
        self.quality_box.set(qualities[0])                        

        self.check_ready() 