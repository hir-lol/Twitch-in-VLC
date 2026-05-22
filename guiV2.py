# gui.py
import subprocess
import customtkinter as ctk
import sys 
import subprocess
import json 
import os
import webbrowser
import shutil

from tkinter import Tk, messagebox
from tkinter import filedialog
from PIL import Image

import threading
import queue

import storage
import asyncio
#=======================
#ФУНКЦИИ
#=======================

def main():
    
    def set_veiw (veiw_name: str):
        if veiw_name == "twitch":
            app.title("Twitch in VLC")
            main_container.tkraise()
            
            btn_twitch.configure(fg_color="#1f6aa5")
            btn_url.configure(fg_color="transparent")
            
        elif veiw_name == "url":
            app.title("URL in VLC")
            url_container.tkraise()
            
            btn_url.configure(fg_color="#1f6aa5")
            btn_twitch.configure(fg_color="transparent")
    
    def get_base_path():
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def resorse_path(relative_path):
        if hasattr(sys, "_MEINPASS"):
            return os.path.join(sys._MEINPASS , relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    CONFIG_FILE = os.path.join(get_base_path()+"/scripts/config.json")
    icon = (get_base_path() + "/assets/ICON.ico")

    def load_config(CONFIG_FILE):
        if not os.path.exists(CONFIG_FILE):
            return {}

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Ошибка чтения config.json:", e)
            return {}
            
    config = load_config(CONFIG_FILE)        

    def on_tab_change():
        tab = tabview.get()
        
        if tab == 'Главный экран':
            app.geometry("300x310")
            print("Смена вкладки на Главный экран 300x260")
        elif tab == 'Настройки':
            app.geometry("500x420")
            print("Смена вкладки на Настройки 500x420")

    def show_error(title: str, message: str):
        root = Tk()
        root.withdraw() #Скрытие пустого окна
        messagebox.showerror(title, message)
        root.destroy()
        
    class get_available_qualities():
        def __init__ (self, twitch_url: str, mode: bool):
            if mode == "module":
                self.module(twitch_url)
            else:
                self.portable(twitch_url)

        def module(self, twitch_url: str):
            from streamlink import Streamlink
            session = Streamlink()
            streams = session.streams(twitch_url)
            data = []
            for quality, stream in streams.items():
                data.append(quality)
            q.put( {
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
                q.put( {
                    "source": "kach",
                    "value": list(data["streams"].keys())
                })
                return
            except subprocess.CalledProcessError as e:            
                print(e)
                error_text = (e.stderr or e.stdout or"").strip()
                if "No playable streams" in error_text:
                    status = "offline"
                else:
                    status = "error"
                q.put( {
                    "source": "kach",
                    "value": [status ,error_text]
                })
                return        
    
    def chek_queue (keys: str, callback):
        line_queue = []
        while not q.empty():
            line = q.get()
            if not isinstance(line, dict):
                continue
            elif line.get("source") == keys:
                callback( line.get("value"))
                return
            else:
                line_queue.append(line)
        for line in line_queue:
            q.put(line)
        app.after(100,lambda: chek_queue(keys, callback))

    class tooltip():
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
        def binds(self):
            self.bind.bind("<Enter>", self.on_enter)
            self.bind.bind("<Leave>", self.on_leave)
        def unbinds(self):
            self.bind.unbind("<Enter>", funcid=None)
            self.bind.unbind("<Leave>", funcid=None)

#===========================
#СОЗДАНИЕ ОКНА И ВКЛАДОК
#===========================

    if "Dark_Theme" in config.get("More_Setting") :
        if(config.get("More_Setting")).get("Dark_Theme") is False:
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("dark")

    app = ctk.CTk()
    app.title("Twitch in VLC")
    app.geometry("300x310")
    app.iconbitmap(icon)

    tabview = ctk.CTkTabview(app)
    tabview.pack(fill="both",expand=True)
    tab_main = tabview.add("Главный экран")
    tab_seting = tabview.add("Настройки")

    root_container = ctk.CTkFrame(tab_main)
    root_container.place(relx = 0 , rely = 0 , relwidth=1,relheight=1)
    
    main_container = ctk.CTkFrame(root_container)
    main_container.place(relx = 0 , rely = 0 , relwidth=1,relheight=1)
    
    url_container = ctk.CTkFrame(root_container)
    url_container.place(relx = 0 , rely = 0 , relwidth=1,relheight=1)

    seting_container = ctk.CTkScrollableFrame(tab_seting)
    seting_container.pack(fill="both",expand=True, padx = 10, pady = 10)

    tabview.configure(command=on_tab_change)
    main_container.tkraise()

    q = queue.Queue()
    qapi = queue.Queue()
    api = storage.ApiWorker(qapi,q)
    api.start()
#==============================
#РАБОТА С ГЛАВНОЙ ВКЛАДКОЙ
#==============================

    class tab_twitch():
        def __init__(self, app, window, q: queue.Queue()):
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

            self.app = window
            self.mode = "twitch"
            self.q = q

        def active_strim_btn(self):
            if not self.stream_running:
                self.stream_running = True
                self.start_stream()
            else:
                if self.core_ready == False:
                    show_error("Ошибка","Ядро ещё не запустилось для закрытия")
                    return
                self.stop_stream()
                self.stream_running = False

        def stop_stream(self):
            if self.core_error == False:
                self.proc.stdin.write("exit\n")
                self.proc.stdin.flush()

            self.start_btn.configure(text=self.start_btn_text,fg_color = "green", state = "disabled")
            
            self.quality_box.configure(state="normal")
            self.quality_box.set("")
            self.quality_box.configure(values=[])
            self.quality_box.set(self.quality_box_text)
            self.quality_box.configure(state = "disabled")
            
            self.url_entry.configure(state="normal")
            self.chat_checkbox.configure(state="normal")
            self.confirm_btn.configure(state="normal")

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

        def check_core_ready(self):
            queues = []
            while not self.q.empty():
                line = self.q.get()
                if not isinstance(line, dict):
                    continue
                elif line.get("source") == "core":
                    line = line.get("value")
                    if line and line == "PROCESS_CLOSED" and self.proc.poll() != None:
                        self.core_ready = True
                        self.core_error = True
                        self.active_strim_btn()
                        self.core_ready_tooltip.unbinds()
                        show_error("Ой","Кажется ядро закрылось раньше чем ожидалось")
                        return
                    if line and "ready" in line:
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
            
            with open(CONFIG_FILE, "r", encoding = "utf-8") as f:
                config = json.load(f)
            
            if self.mode == "twitch":
                config["mode"] = [(config["mode"])[0],self.mode]
                config["channel"] = channel
                config["kach"] = quality
                config["otv"] = bool(open_chat)
            else:
                url = "https://" + channel
                config["mode"] = [(config["mode"])[0],self.mode]
                config["URL"] = url
                config["URL_KACH"] = quality
            
            with open(CONFIG_FILE, "w", encoding = "utf-8") as f:
                json.dump(config, f, indent=4,ensure_ascii=False)
                
            core_pat = os.path.join(get_base_path()+"/scripts/core.py")
            self.proc = subprocess.Popen(["python",core_pat], shell= False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)

        def check_ready(self):
            channel_ok = bool(self.url_entry.get().strip())
            quality_ok = bool(self.quality_box.get().strip())

            if channel_ok and quality_ok:
                self.start_btn.configure(state="normal")
                self.start_btn.configure(fg_color = "green")
            else:
                self.start_btn.configure(state="disabled")

        def on_channel_confirm(self):
            if (config.get("mode"))[0] =="portable":
                if not shutil.which("streamlink"):
                    show_error("Streamlink не найден","Streamlink не обнаружен в PATH\nУстановите Streamlink и перезапустите программу")
                    return
            
            if self.mode == "twitch":
                channel = self.url_entry.get().strip().lower()
            else:
                channel = self.url_entry.get().strip()

            if not channel:
                print("Введите никнейм")
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
            threading.Thread(target=lambda: get_available_qualities(twitch_url,(config.get("mode"))[0]),daemon=True).start() 
            chek_queue("kach", self.edit_qualities)

        def edit_qualities(self, qualities: list):

            if not qualities or qualities[0] == "offline" or qualities[0] == "error":
                if not qualities:
                    pass
                else:
                    print(qualities[1])
                show_error("Ошибка проверки доступных качеств", "Не удалось получить настройки качества, возможно эфир офлайн.\n Или видён некоректный никнейм/название")
                self.quality_box.configure(state = "normal")
                self.quality_box.set("")
                self.quality_box.configure(state = "disabled")      
                self.confirm_btn.configure(state="normal")      
                self.url_entry.configure(state = "normal")
                return

            self.quality_box.configure(values=qualities)
            self.quality_box.configure(state = "readonly")
            self.quality_box.set("")
            self.quality_box.set(qualities[0])                        

            self.check_ready() 
    
    main_tab = tab_twitch(app=main_container, window=app, q=q)

    icon_main = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/icon1v.png"), dark_image = Image.open(get_base_path()+"/assets/icon1v.png"), size = (22,22))
    icon_url = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/icon2v.png"), dark_image = Image.open(get_base_path()+"/assets/icon2v.png"), size = (22,22))
    
    side_panel_in_main = ctk.CTkFrame(main_container, width = 30 ,height = 90, corner_radius = 10)
    side_panel_in_main.pack_propagate(False)
    side_panel_in_main.place(x = 20 , rely = 0.474, anchor = "center", relheight = 0.39)
    
    btn_twitch = ctk.CTkButton(side_panel_in_main,image = icon_main,text="",width=40,height=40,fg_color="#1f6aa5",hover_color="#3a3a3a",command=lambda: set_veiw("twitch"))
    btn_twitch.pack(pady=8)
    btn_url = ctk.CTkButton(side_panel_in_main,image = icon_url,text="",width=40,height=40,fg_color="transparent",hover_color="#3a3a3a",command=lambda: set_veiw("url"))
    btn_url.pack(pady=8)
    
    side_panel_in_url = ctk.CTkFrame(url_container, width = 30 ,height = 90, corner_radius = 10)
    side_panel_in_url.pack_propagate(False)
    side_panel_in_url.place(x = 20 , rely = 0.474, anchor = "center", relheight = 0.39)
    
    btn_twitch = ctk.CTkButton(side_panel_in_url,image = icon_main,text="",width=40,height=40,fg_color="#1f6aa5",hover_color="#3a3a3a",command=lambda: set_veiw("twitch"))
    btn_twitch.pack(pady=8)
    btn_url = ctk.CTkButton(side_panel_in_url,image = icon_url,text="",width=40,height=40,fg_color="transparent",hover_color="#3a3a3a",command=lambda: set_veiw("url"))
    btn_url.pack(pady=8)
    
    url_tab = tab_twitch(app=url_container, window=app, q=q)
    url_tab.mode = "url"
    url_tab.start_btn_text = "Play URL"
    url_tab.stop_btn_text = "Stop playing"
    url_tab.chat_checkbox.pack_forget()
    url_tab.tooltip_url_entry.edit_text("Ведите ссылку на ресурс\nНа котором ведётся\nПрямой эфир")
    url_tab.confirm_btn.configure(text="Получить качества")
    url_tab.url_entry.configure(placeholder_text="https://...")
    url_tab.quality_box_text = "Получите качества снова"

#======================
#ВКЛАДКА С ЗАПИСАНАМИ КАНАЛАМИ
#======================

    class saves_channels():
        def __init__(self, app):
            self.app = ctk.CTkToplevel(app)
            self.app.title("Сохранёные")
            self.app.geometry("350x310")
            self.app.after (200, lambda: self.app.iconbitmap(icon))
            self.app.protocol("WM_DELETE_WINDOW", lambda: self.tab())
            self.app_tab = False
            self.app.withdraw()

            self.top_frame = ctk.CTkFrame(self.app)
            self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            self.top_frame.grid_columnconfigure(0, weight=1)

            self.placeholder_channels = ctk.CTkEntry(
                self.top_frame,
                placeholder_text = "Никнейм канала"
            )
            self.placeholder_channels.grid(row=0, column=0, sticky="ew")
            self.placeholder_channels.bind("<Return>", lambda e: self.edit_channels_activate())

            self.Button_channels = ctk.CTkButton(self.top_frame, text="Добавить",width=80, command=lambda:self.edit_channels_activate())
            self.Button_channels.grid(row=0, column=1)            

            self.middle_frame = ctk.CTkScrollableFrame(self.app)
            self.middle_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

            self.update_channels_button = ctk.CTkButton(self.app,text="Обновить каналы", command=lambda:self.update_list_channels())
            self.update_channels_button.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
            self.app.grid_rowconfigure(1, weight=1)
            self.app.grid_columnconfigure(0, weight=1)

            self.channel_frame = {}

            self.delete_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/delete.png"), dark_image = Image.open(get_base_path()+"/assets/delete.png"))
            self.play_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/play.png"), dark_image = Image.open(get_base_path()+"/assets/play.png"))

        def tab(self):
            if not self.app_tab:
                self.app_tab = True
                self.app.deiconify()
                self.update_list_channels()
            else :
                self.app_tab = False 
                self.app.withdraw()

        def activate_lef_btn(self, channel: str):
            print("Вписываем и нажимаем кнпоку")
            self.url_entry.delete(0, ctk.END)
            self.url_entry.insert(0, channel)
            self.on_channel_confirm()
            self.tab()

        def setting_add(self, communicate_object: ctk.CTkEntry, communicate_def):
            self.url_entry = communicate_object
            self.on_channel_confirm = communicate_def

        def delete_channels (self, channel: str):
            print("DELETE")
            list_channels = storage.read_channels()
            if channel in list_channels:
                list_channels.remove(channel)
            storage.edit_channels(list_channels)
            self.update_list_channels()

        def create_channel_row(self, parent, channel: str, data: dict):
            print(f"Создаю контейнер для {channel}")
            row_frame = ctk.CTkFrame(parent)
            row_frame.pack(fill="x",padx=5,pady=2)

            top_frame = ctk.CTkFrame(row_frame)
            top_frame.pack(fill="x")

            left_btn = ctk.CTkButton(top_frame,image=self.play_image,text="",width=28,height=28,command=lambda:self.activate_lef_btn(channel))
            left_btn.pack(side="left",padx=(5,10))

            channel_name_label = ctk.CTkLabel(top_frame,text=channel)
            channel_name_label.pack(side="left",padx=10)

            is_live = data.get("lives")
            if is_live == True:
                status_text = "Онлайн"
            elif is_live == "error":
                status_text = "Ошибка"
            else:
                status_text = "Офлайн"
            status_label = ctk.CTkLabel(top_frame,text=status_text)
            status_label.pack(side="left",padx=10)

            delete_btn = ctk.CTkButton(top_frame,image=self.delete_image,text="",width=28,height=28,fg_color="black",command=lambda:self.delete_channels(channel))
            delete_btn.pack(side="right",padx=5) 

            if is_live == True:
                left_btn.configure(fg_color="green")

                botton_frame = ctk.CTkFrame(row_frame)
                botton_frame.pack(fill="x",padx=10,pady=(2,5))
                
                text_game_label = data.get("game")
                game_label = ctk.CTkLabel(botton_frame)
                if len(text_game_label) > 10:
                    tooltip_game_label = tooltip(text=text_game_label, app = self.app, bind = game_label)
                    game_label.configure(text="Категория")
                else: 
                    game_label.configure(text=f"Категория:{text_game_label}")
                game_label.pack(side="left",padx=5)

                text_viewer_label = data.get("viewercount")
                viewer_label = ctk.CTkLabel(botton_frame,text=f"Зритилей:{text_viewer_label}")
                viewer_label.pack(side="left",padx=5)

                text_title_label = data.get("title")
                title_label = ctk.CTkLabel(botton_frame,text="Тайтл")
                title_label.pack(side="left",padx=5)
                
                tooltip_title_label = tooltip(text=text_title_label, app=title_label,bind=title_label)      
            else:
                if is_live == "error":
                    left_btn.configure(fg_color="red")
                    tooltip(text="Ошибка при обработке запроса",app=left_btn,bind=left_btn)
                left_btn.configure(state="disabled")
                botton_frame = None

            self.channel_frame[channel] = {
                "frame":row_frame,
                "top_frame":top_frame,
                "status_label": status_label,
                "botton_frame": botton_frame
            }
    
        def edit_channels_activate(self):
            channel_name = self.placeholder_channels.get().strip()
            if not channel_name:
                print('пусто')
                return
            
            self.placeholder_channels.delete(0, ctk.END)
            print("сохраняю")
            channels_list = storage.read_channels()
            channels_list.append(channel_name)
            storage.edit_channels(channels_list)
            self.update_list_channels()

        def update_list_channels(self):
            print("Обновляется список")
            for widget in self.middle_frame.winfo_children():
                widget.destroy()
            channels_list = storage.read_channels()
            if channels_list == None:
                return
            self.placeholder_channels.configure(placeholder_text="Обновляется список")
            self.placeholder_channels.configure(state = "disabled")
            self.Button_channels.configure(state = "disabled")
            self.update_channels_button.configure(state = "disabled")
            #threading.Thread(target=lambda: asyncio.run(storage.get_channels_info("saves",channels_list,q)),daemon=True).start()
            qapi.put({
                "source" : "channels_info",
                "value" : ["saves",channels_list]
            })
            chek_queue("info_channel_key", self.update)        

        def update(self, data: list):
            if data[0] == "done":
                self.placeholder_channels.configure(state = "normal",placeholder_text="Никнейм канала")
                self.Button_channels.configure(state = "normal")
                self.update_channels_button.configure(state = "normal")
                return
            elif data[0] not in storage.read_channels():
                self.keys = data[0]
            else:
                self.create_channel_row(self.middle_frame,channel=data[0],data=data[1])
            chek_queue(self.keys, self.update)

    saves_tabs = saves_channels(app)
    saves_tabs.setting_add(communicate_object = main_tab.url_entry, communicate_def = main_tab.on_channel_confirm)

    tab_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/saves.png"), dark_image = Image.open(get_base_path()+"/assets/saves.png"), size = (20,20))
    channels_Button = ctk.CTkButton(
        main_container,
        image = tab_image,
        width = 20,
        height = 20,
        text = "",
        hover=False,
        corner_radius=10,
        command=lambda:saves_tabs.tab()
    )
    channels_Button.place(relx = 1, rely = 0,anchor="ne", x = -10, y = 20)
    tooltip_channels_Button = tooltip(text="Сохранёные каналы",app=app,bind=channels_Button)

#======================
#ВКЛАДКА С ИНФОРМАЦИЕЙ О КАНАЛЕ
#======================

    class info_channels():
        def __init__(self,app):
            self.app = ctk.CTkToplevel(app)
            self.app.title("Информация о канале")
            self.app.geometry("350x310")
            self.app.after (200, lambda: self.app.iconbitmap(icon))
            self.app.protocol("WM_DELETE_WINDOW", lambda: self.tab())
            self.app_tab = False
            self.app.withdraw()

            self.top_frame = ctk.CTkFrame(self.app)
            self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

            self.entry_channels = ctk.CTkEntry(self.top_frame, placeholder_text="Никнейм")
            self.entry_channels.grid(row=0, column=0, sticky="ew")

            self.Button_channels = ctk.CTkButton(self.top_frame, text="Проверить",width=80, command=lambda:show_error("Скоро","Ещё не доделал"))
            self.Button_channels.grid(row=0, column=1)

            self.top_frame.grid_columnconfigure(0, weight=1)

            self.app.grid_rowconfigure(1, weight=1)
            self.app.grid_columnconfigure(0, weight=1)

        def tab(self):
            if self.app_tab == False:
                self.app_tab = True
                self.app.deiconify()
            else :
                self.app_tab = False 
                self.app.withdraw()

    info_channels_frame = info_channels(app)
    tab_info_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/info.png"), dark_image = Image.open(get_base_path()+"/assets/info.png"), size = (20,20))
    channels_info_Button = ctk.CTkButton(
        main_container,
        image = tab_info_image,
        width = 20,
        height = 20,
        text = "",
        hover=False,
        corner_radius=10,
        command=lambda:info_channels_frame.tab()
    )
    channels_info_Button.place(relx = 1, rely = 0,anchor="ne", x = -10, y = 50)

    channels_info_tooltip = tooltip(text="Информация о канале\nСкоро", app=app,bind=channels_info_Button)

#======================
#ВКЛАДКА СООБЩЕСТВА
#======================

    class info_team():
        def __init__(self,app):
            self.main_app = app
            self.app = ctk.CTkToplevel(app)
            self.app.title("Информация о сообществе")
            self.app.geometry("370x310")
            self.app.after (200, lambda: self.app.iconbitmap(icon))
            self.app.protocol("WM_DELETE_WINDOW", lambda: (self.app.withdraw(), setattr(self,"app_tab",False)))
            self.app_tab = False
            self.app.withdraw()

            self.tabview = ctk.CTkTabview(self.app,command=self.on_tab_change)
            self.tabview.pack(fill="both",expand=True)
            self.tab_main = self.tabview.add("Найти")

            self.get_mode()
            self.tabs_frame = {}
            self.tabview_status = [False]
            self.tabs_click_count = {}
            self.tabs = storage.read_tabs()
            if self.tabs != None:
                self.delete_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/delete.png"), dark_image = Image.open(get_base_path()+"/assets/delete.png"))
                self.play_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/play.png"), dark_image = Image.open(get_base_path()+"/assets/play.png"))
                for key in self.tabs:
                    container_tabs = self.tabview.add(key)
                    container_tabs.grid_rowconfigure(1, weight=1)
                    container_tabs.grid_columnconfigure(0, weight=1)
                    container_tab = ctk.CTkScrollableFrame(container_tabs)
                    container_tab.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
                    self.tabs_frame[key] = container_tab
                    self.tabs_click_count[key] = 0

            self.top_frame = ctk.CTkFrame(self.tab_main)
            self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

            self.entry_channels = ctk.CTkEntry(self.top_frame, placeholder_text="Название сообщества")
            self.entry_channels.grid(row=0, column=0, sticky="ew")
            self.entry_channels.bind("<Return>", lambda e:self.get_team(frame=self.middle_frame,app=app))

            self.Button_channels = ctk.CTkButton(self.top_frame, text="Узнать",width=80, command=lambda:self.get_team(frame=self.middle_frame,app=app))
            self.Button_channels.grid(row=0, column=1)

            self.top_frame.grid_columnconfigure(0, weight=1)

            self.tab_main.grid_rowconfigure(1, weight=1)
            self.tab_main.grid_columnconfigure(0, weight=1)
        
            self.middle_frame = ctk.CTkScrollableFrame(self.tab_main)
            self.middle_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

            self.button_frame = ctk.CTkFrame(self.tab_main)
            self.button_frame.grid(row=2,column=0,columnspan=3,sticky="ew",padx=10,pady=1)
            self.button_frame.grid_columnconfigure((0,1,2),weight=1)

            self.team_info = None

            self.add_button = ctk.CTkButton(self.button_frame,text="Добавить", command=lambda:self.add_in_saves())
            self.add_button.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
            self.add_button_tooltip = tooltip(text="Добавить все в сохранёные",app=app,bind=self.add_button)

            self.add_if_button = ctk.CTkButton(self.button_frame,text="Добавить..",command=lambda:self.add_in_saves_if())
            self.add_if_button.grid(row=2, column=2,sticky="ew",padx=5,pady=5)
            self.add_if_button_tooltip = tooltip(text="Добавить в сохранёные\nДобавит те каналы которых\nНету в сохранёных",app=app,bind=self.add_if_button)

            self.add_in_button = ctk.CTkButton(self.button_frame,text="Добавить в..", command=lambda:self.add_in_tabs(app=app))
            self.add_in_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
            self.add_in_button_tooltip = tooltip(text="Добавить во вкладку в\nЭтом окне",app=app,bind=self.add_in_button)

        def get_mode(self):
            if "Team_mode" in config.get("More_Setting"):
                if (config.get("More_Setting")).get("Team_mode") is True:
                    self.mode = True
                else:
                    self.mode = False
            else:
                self.mode = False

        def activate_lef_btn(self, channel: str):
            print("Вписываем и нажимаем кнпоку")
            self.url_entry.delete(0, ctk.END)
            self.url_entry.insert(0, channel)
            self.on_channel_confirm()
            self.tab()

        def delete_channels (self, channel: str):
            print("DELETE")
            list_channels = (storage.read_tabs()).get(self.tabview.get())
            if channel in list_channels:
                list_channels.remove(channel)
            storage.edit_tabs(list_channels)
            self.update_list_tabview(self.tabview.get())

        def create_channel_row(self, parent, channel: str, data: dict):
            print(f"Создаю контейнер для {channel}")
            row_frame = ctk.CTkFrame(parent)
            row_frame.pack(fill="x",padx=5,pady=2)

            top_frame = ctk.CTkFrame(row_frame)
            top_frame.pack(fill="x")

            left_btn = ctk.CTkButton(top_frame,image=self.play_image,text="",width=28,height=28,command=lambda:self.activate_lef_btn(channel))
            left_btn.pack(side="left",padx=(5,10))

            channel_name_label = ctk.CTkLabel(top_frame,text=channel)
            channel_name_label.pack(side="left",padx=10)

            is_live = data.get("lives")
            if is_live == True:
                status_text = "Онлайн"
            elif is_live == "error":
                status_text = "Ошибка"
            else:
                status_text = "Офлайн"
            status_label = ctk.CTkLabel(top_frame,text=status_text)
            status_label.pack(side="left",padx=10)

            delete_btn = ctk.CTkButton(top_frame,image=self.delete_image,text="",width=28,height=28,fg_color="black",command=lambda:self.delete_channels(channel))
            delete_btn.pack(side="right",padx=5)

            info_btn = ctk.CTkButton(top_frame,image=tab_info_image,text="",width=28,height=28,command=lambda:self.chek_info_channel(channel))
            info_btn.pack(side="right",padx=5)

            if is_live == True:
                left_btn.configure(fg_color="green")

                botton_frame = ctk.CTkFrame(row_frame)
                botton_frame.pack(fill="x",padx=10,pady=(2,5))
                
                text_game_label = data.get("game")
                game_label = ctk.CTkLabel(botton_frame)
                if len(text_game_label) > 10:
                    tooltip_game_label = tooltip(text=text_game_label, app = self.app, bind = game_label)
                    game_label.configure(text="Категория")
                else: 
                    game_label.configure(text=f"Категория:{text_game_label}")
                game_label.pack(side="left",padx=5)

                text_viewer_label = data.get("viewercount")
                viewer_label = ctk.CTkLabel(botton_frame,text=f"Зритилей:{text_viewer_label}")
                viewer_label.pack(side="left",padx=5)

                text_title_label = data.get("title")
                title_label = ctk.CTkLabel(botton_frame,text="Тайтл")
                title_label.pack(side="left",padx=5)
                
                tooltip_title_label = tooltip(text=text_title_label, app=title_label,bind=title_label)      
            else:
                if is_live == "error":
                    left_btn.configure(fg_color="red")
                    tooltip(text="Ошибка при обработке запроса",app=left_btn,bind=left_btn)
                left_btn.configure(state="disabled")

        def on_tab_change(self):
            if self.tabview_status[0] == True:                
                self.tabview.set(self.tabview_status[1])
                show_error("Недопустимо","Дождитесь пока список полностью обновится")
                return
            name_tab = self.tabview.get()
            if name_tab == "Найти":
                return
            self.tabs_click_count[name_tab] += 1
            if self.tabs_click_count[name_tab] == 1:
                if self.mode is True: 
                    self.update_list_tabview(name_tab)
                else: 
                    self.container_tab = self.tabs_frame.get(name_tab)
                    if self.container_tab == None:
                        show_error("Ошибка","Произошла ошибка при обновлении содержимого вкладки\nПроверьте существует ли содержимое для данной вкладки")
                        return
                    for widget in self.container_tab.winfo_children():
                        widget.destroy()
                    self.add_team(self.tabs.get(name_tab),self.container_tab,self.main_app)                    

            if self.tabs_click_count[name_tab] >= 5:
                self.tabs_click_count[name_tab] = 0

        def update_list_tabview(self, name_tab: str):
            self.container_tab = self.tabs_frame.get(name_tab)
            if self.container_tab == None:
                show_error("Ошибка","Произошла ошибка при обновлении содержимого вкладки\nПроверьте существует ли содержимое для данной вкладки")
                return
            for widget in self.container_tab.winfo_children():
                widget.destroy()
            #threading.Thread(target=lambda: asyncio.run(storage.get_channels_info(name_tab, self.tabs.get(name_tab),q)),daemon=True).start()
            qapi.put({
                "source" : "channels_info",
                "value" : [name_tab,self.tabs.get(name_tab)]
            })
            self.tabview_status = [True,name_tab]
            chek_queue("info_channel_key", self.update)    

        def update(self, data: list):
            name_tab = self.tabview.get()
            if data[0] == "done":
                self.tabview_status = [False]
                print("Обновление списка завершено")
                return            
            elif data[0] not in self.tabs.get(name_tab):
                self.key = data[0]
            else:
                self.create_channel_row(self.container_tab,channel=data[0],data=data[1])
            chek_queue(self.key, self.update)    

        def add_in_tabs(self,app):
            if self.team_info == None:
                show_error("Ошибка при добавлении в сохранёное","Нечего добовлять")
                return
            self.data = storage.read_tabs()
            self.data[self.entry_channels.get().strip()] = self.team_info
            storage.edit_tabs(self.data)
            self.app.destroy()
            self.__init__(app=app)
            self.tab()

        def add_in_saves_if(self):
            if self.team_info == None:
                show_error("Ошибка при добавлении в сохранёное","Нечего добовлять")
                return
            channels = storage.read_channels()
            list_lower = set(item.lower() for item in channels)
            print(list_lower)
            for item in self.team_info:
                if item.lower() not in list_lower:
                    channels.append(item)
                    list_lower.add(item.lower())
            storage.edit_channels(channels)
            self.tab()

        def add_in_saves(self):
            if self.team_info == None:
                show_error("Ошибка при добавлении в сохранёное","Нечего добовлять")
                return
            channels = storage.read_channels()
            channels.extend(self.team_info)
            storage.edit_channels(channels)
            self.tab()

        def get_team(self, frame,app):
            team = self.entry_channels.get().strip().lower()
            #self.team_info = asyncio.run(storage.get_team(team))
            qapi.put({
                "source": "get_team",
                "value": team
            })
            chek_queue("get_team", lambda a :self.add_team(a,frame,app))

        def add_team (self, team_info, frame, app):
            self.plays_button_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/plays.png"), dark_image = Image.open(get_base_path()+"/assets/plays.png"), size = (20,20))
            self.add_button_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/add.png"), dark_image = Image.open(get_base_path()+"/assets/add.png"), size = (20,20))
            for channel in team_info:
                print(f"Создаю для {channel}")
                self.draw_channel(channel=channel,frame=frame,app=app)

        def draw_channel(self, channel: str, frame, app):
            frame_channel = ctk.CTkFrame(frame)
            frame_channel.pack(fill="x",padx=2,pady=2)

            channel_label = ctk.CTkLabel(frame_channel,text=channel)
            channel_label.pack(side="left",padx=10)

            info_channel_button = ctk.CTkButton(frame_channel,image=tab_info_image,width=20,height=20,text="",corner_radius=10,command=lambda:self.chek_info_channel(channel))
            info_channel_button.pack(side="right",padx=2)
            info_channel_button_tooltip = tooltip(text="Узнать информация о канале",app=app,bind=info_channel_button)

            add_channel_button = ctk.CTkButton(frame_channel,image=self.add_button_image,width=20,height=20,text="",corner_radius=10)
            add_channel_button.pack(side="right",padx=2)
            add_channel_button_tooltip = tooltip(text="Добавить в сохранёные",app=app,bind=add_channel_button)
            add_channel_button.configure(command=lambda:self.add_channel_in_saves(channel=channel,tooltip=add_channel_button_tooltip))

            self.status_channel = {}
            play_channel_button = ctk.CTkButton(frame_channel,image=self.plays_button_image,width=20,height=20,text="",corner_radius=10)
            play_channel_button.pack(side="right",padx=2)
            self.default_color = play_channel_button.cget("fg_color")
            play_channel_button_tooltip = tooltip(text="Узнать стримит ли",app=app,bind=play_channel_button)
            play_channel_button.configure(command=lambda:self.is_lives(button=play_channel_button,channel=channel,tooltip=play_channel_button_tooltip))

        def add_channel_in_saves(self,channel: str,tooltip: tooltip):
            saves = storage.read_channels()
            saves.append(channel)
            storage.edit_channels(saves)
            tooltip.edit_text(text="Добавлено")

        def is_lives(self,button : ctk.CTkButton,channel : str, tooltip: tooltip):
            status = self.status_channel.get(channel)
            if status == True:
                self.activate_lef_btn(channel)
            else:
                #status_new = asyncio.run(storage.is_lives(channel))
                qapi.put({
                    "source": "is_lives",
                    "value": channel 
                })
                tooltip.edit_text(text="Проверка")
                chek_queue("is_lives", lambda a:self.add_is_lives(button,channel,tooltip,a))

        def add_is_lives(self,button : ctk.CTkButton,channel : str, tooltip: tooltip, status_new):
            if status_new == True:
                tooltip.edit_text(text="Стримит, можно воспроизвести")
                button.configure(fg_color="green")
                self.status_channel[channel] = status_new
            else:
                tooltip.edit_text(text="Не стримит, проверить снова?")
                button.configure(fg_color=self.default_color)
                self.status_channel[channel] = status_new

        def chek_info_channel(self,channel: str):
            print(f"Вписываю {channel} в поле")
            self.communicate_object.delete(0, ctk.END)
            self.communicate_object.insert(0, channel)
            self.tab()
            self.window_info_channels.tab()

        def setting_add(self,communicate_object: ctk.CTkEntry, window : info_channels, communicate_object_2: ctk.CTkEntry, communicate_def):
            self.communicate_object = communicate_object
            self.window_info_channels = window
            self.url_entry = communicate_object_2
            self.on_channel_confirm = communicate_def

        def tab(self):
            if self.app_tab == False:
                self.app_tab = True
                self.app.deiconify()
            else :
                self.app_tab = False 
                self.app.withdraw()

    info_team_frame = info_team(app)
    info_team_frame.setting_add(communicate_object =info_channels_frame.entry_channels, window = info_channels_frame, communicate_object_2 = main_tab.url_entry, communicate_def = main_tab.on_channel_confirm)
    tab_info_team_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/team.png"), dark_image = Image.open(get_base_path()+"/assets/team.png"), size = (20,20))
    team_info_Button = ctk.CTkButton(
        main_container,
        image = tab_info_team_image,
        width = 20,
        height = 20,
        text = "",
        hover=False,
        corner_radius=10,
        command=lambda:info_team_frame.tab()
    )
    team_info_Button.place(relx = 1, rely = 0,anchor="ne", x = -10, y = 80)

    team_info_tooltip = tooltip(text="Информация о сообществах", app=app,bind=team_info_Button)

#======================
#НАСТРОЙКИ
#======================

    class add_arg_setting():
        """
        Класс для окна с аргументами запуска streamlink
        """
        def __init__(self, app=ctk.CTk):
            self.arg_app = ctk.CTkToplevel(app)
            self.arg_app.title("Дополнительные аргументы")
            self.arg_app.geometry("350x310")
            self.arg_app.after (200, lambda: self.arg_app.iconbitmap(icon))
            self.arg_app.protocol("WM_DELETE_WINDOW", lambda: self.arg_tab())
            self.arg_app_tab = False
            self.arg_app.withdraw()

            self.top_frame = ctk.CTkFrame(self.arg_app)
            self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

            self.entry_arg = ctk.CTkEntry(self.top_frame, placeholder_text="Аргумент")
            self.entry_arg.grid(row=0, column=0, sticky="ew")
            self.entry_arg.bind("<Return>", lambda e:self.add_in_arg())

            self.Button_arg = ctk.CTkButton(self.top_frame, text="Добавить",width=80, command=lambda:self.add_in_arg())
            self.Button_arg.grid(row=0, column=1)

            self.top_frame.grid_columnconfigure(0, weight=1)

            self.arg_app.grid_rowconfigure(1, weight=1)
            self.arg_app.grid_columnconfigure(0, weight=1)

            self.Main_Frame = ctk.CTkScrollableFrame(self.arg_app)
            self.Main_Frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
            self.check_arg()
            self.draw_arg()

        def get_var(self) -> dict:
            args = []
            for item in self.var :
                arg = {
                    "text": item[0],
                    "value": (item[1]).get(),
                    "tooltip": item[2]
                }
                args.append(arg)
            return args

        def add_in_arg(self):
            arg = self.entry_arg.get().strip()
            if not arg:
                show_error("Запрещено","Нельзя добавить пустоту")
                return
            self.entry_arg.delete(0, ctk.END)
            print("Сохранение:",arg)
            arg_dict = {"text" : arg}
            self.args.append(arg_dict)
            self.draw_arg()

        def check_arg(self):
            config = load_config(CONFIG_FILE)            
            try:
                args = config.get("More_Setting")
                self.args = args.get("Custom_arg")
            except Exception as e:
                print("ERROR in add_arg_setting:",e)
                self.args = []

        def draw_arg(self):
            for widget in self.Main_Frame.winfo_children():
                widget.destroy()
            if self.args is None:
                self.args = []
            print("Начало отрисовки аргументов")
            self.var = []
            for arg in self.args:
                try:
                    text = arg.get("text")
                    value = arg.get("value") 
                    arg_tooltip = arg.get("tooltip")

                    print("Отрисовка для",text)

                    if value is True:
                        vars = ctk.BooleanVar(value=True)
                    else:
                        vars = ctk.BooleanVar()

                    ChecBox = ctk.CTkCheckBox(self.Main_Frame,text=text,variable=vars)
                    ChecBox.pack(padx=5,pady=6,anchor="w")
                    if arg_tooltip is not None:
                        arg_tooltips = tooltip(arg_tooltip,self.arg_app,ChecBox)

                    if arg_tooltip is not None:
                        saves = [text, vars, arg_tooltip]
                    else: 
                        saves = [text, vars, None]

                    self.var.append(saves)

                except Exception as e :
                    show_error("Ой","Ошибка при создании виджетов для аргументов")
                    print("ERROR при отресовки:\n", e)
            print("Конец отрисовки")

        def arg_tab(self):
            if self.arg_app_tab is False:
                self.arg_app_tab = True
                self.arg_app.deiconify()
            else :
                self.arg_app_tab = False 
                self.arg_app.withdraw()

    class dop_setting():
        """
        Класс для дополнительных настроек по нажатию
        """
        def __init__(self, app=ctk.CTkFrame, mode=str):
            self.var=[]
            self.tab_in = False
            self.app = app
            self.mode = mode
            if self.mode == "portable":
                self.add_arg_window(False)
            self.get_config()
            self.Add_Main_Objects()
            self.Add_Setting_Objects()

        def get_config(self):
            try:
                config = load_config(CONFIG_FILE)
                self.mods = config.get("More_Setting")
                if self.mods is None:
                    self.mods = {}
            except Exception as e :
                self.mods = {}
                print("ERROR in dopsetting/get_config:\n",e)

        def get(self) -> dict:
            arg = {}
            for item in self.var:
                arg[item.get("tip")] = (item.get("var")).get()
            if self.mode == "portable":
                item = self.app_arg.get_var()
                arg["Custom_arg"] = item
            return arg

        def Add_Setting_Objects(self):
            self.Main_Frame = ctk.CTkFrame(self.app)

            if self.mods.get("Dark_Theme") is True:
                self.Dark_Theme_var = ctk.BooleanVar(value=True)
            else:
                self.Dark_Theme_var = ctk.BooleanVar()
            self.Dark_Theme_CheckBox = ctk.CTkCheckBox(self.Main_Frame,text="Тёмная тема приложения",variable=self.Dark_Theme_var)
            self.Dark_Theme_CheckBox.pack(pady=7,padx=5,anchor="w")
            self.var.append({
                "tip": "Dark_Theme",
                "var": self.Dark_Theme_var
            })

            if self.mods.get("Team_mode") is True:
                self.Team_var = ctk.BooleanVar(value=True)
            else: 
                self.Team_var = ctk.BooleanVar()
            self.Team_CheckBox = ctk.CTkCheckBox(self.Main_Frame,text="Другой режим в Team",variable=self.Team_var)
            self.Team_tooltip = tooltip("Переключить режим в сохранёных сообществах\nПо умолчанию будет как в поиске сообществ\nВ ином случае будет как в сохранёных каналах",self.app,self.Team_CheckBox)
            self.Team_CheckBox.pack(pady=7,padx=5,anchor="w")
            self.var.append({
                "tip" : "Team_mode",
                "var" : self.Team_var
            })

            if self.mode == "portable":
                self.add_arg_window(True)

        def add_arg_window (self, value = bool):
            if value is False:
                self.app_arg = add_arg_setting(self.app)
            else:
                self.agg_arg_frame = ctk.CTkFrame(self.Main_Frame)
                self.agg_arg_frame.pack(pady=7,padx=5,anchor="w")

                self.Image_arg = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/info.png"), dark_image = Image.open(get_base_path()+"/assets/info.png"), size = (20,20))
                self.agg_arg_Button = ctk.CTkButton(
                    self.agg_arg_frame,
                    text = "",
                    image= self.Image_arg,
                    width=20,
                    command=lambda: self.app_arg.arg_tab()
                )
                self.agg_arg_Button.grid(row=0,column=0,padx=5,pady=5)

                self.agg_arg_Label = ctk.CTkLabel(self.agg_arg_frame,text="Дополнительные аргументы")
                self.agg_arg_Label.grid(row=0,column=1,padx=5,pady=5)
                self.agg_arg_Tooltip = tooltip("Дополнительные аргументы при запуске стримов",self.app,self.agg_arg_Label)

        def get_seting(self):
            value = {}
            for item in self.var :
                value[item.get("tip")] = item.get("var")
            return value

        def tab(self):
            try:
                if self.tab_in is False:
                    self.Main_Frame.pack(fill="x", pady=5, padx=3,anchor="w")
                    self.Main_Button.configure(image=self.Image_open)
                    self.tab_in = True
                else:
                    self.Main_Frame.pack_forget()
                    self.Main_Button.configure(image=self.Image_close)
                    self.tab_in = False
            except Exception as e :
                show_error("Ошибка","Ошибка при раскрытии контейнера с доп настройками")
                print("ERROR:\n", e)

        def Add_Main_Objects(self):
            self.Main_Frame_Button = ctk.CTkFrame(self.app)
            self.Main_Frame_Button.pack( pady=5, padx=3)

            self.Image_close = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/1.png"), dark_image = Image.open(get_base_path()+"/assets/1.png"), size = (20,20))
            self.Image_open = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/2.png"), dark_image = Image.open(get_base_path()+"/assets/2.png"), size = (20,20))

            self.Main_Button = ctk.CTkButton(
                self.Main_Frame_Button,
                text = "",
                image= self.Image_close,
                width=20,
                command=lambda: self.tab()
            )
            self.Main_Button.grid(row=0,column=0,padx=5,pady=5)

            self.Main_Label = ctk.CTkLabel(self.Main_Frame_Button,text="Дополнительные настройки")
            self.Main_Label.grid(row=0,column=1,padx=10,pady=5)

    class setings_tabs():
        def __init__ (self, app, container):
            self.app = app            
            self.container = container
            ctk.CTkLabel(container, text="Путь к VLC").pack(anchor="w")

            self.vlc_entry = ctk.CTkEntry(
                container,
                placeholder_text="C:/Program Files/VideoLAN/VLC/vlc.exe"
            )
            self.vlc_entry.pack(fill="x", pady=(0, 5))
            if "VLC_PATH" in config  and config.get("VLC_PATH") != "":
                self.vlc_entry.insert(0,config["VLC_PATH"])

            self.tooltip_vlc_entry = tooltip(text="Обязательное поле",app=app,bind=self.vlc_entry)

            ctk.CTkButton(
                container,
                text="Обзор",
                command=lambda: self.browse_exe(self.vlc_entry)
            ).pack(anchor="e", pady=(0, 10))

            ctk.CTkLabel(container,text="Клиент чата").pack(anchor="w")
            self.chat = ctk.CTkComboBox(
                container,
                values=["Chatterino","Браузер","Другой"], state="readonly"
            )
            self.chat.pack(anchor="w", pady=(0, 15))
            self.chat_tooltip = tooltip(text="Если использовать браузер то он не будет закрываться",app=app,bind=self.chat)
            if config.get("chat") in self.chat.cget("values"):
                self.chat.set(config.get("chat"))

            if config.get("chat") != "Браузер":

                if config.get("chat") == "Chatterino":
                    ctk.CTkLabel(container, text="Путь chatterino").pack(anchor="w")
                else:
                    ctk.CTkLabel(container, text="Путь к клиенту чата ").pack(anchor="w")

                self.chat_entry = ctk.CTkEntry(
                    container,
                    placeholder_text="C:/Program Files/Chatterino/chatterino.exe"
                )
                self.chat_entry.pack(fill="x", pady=(0, 15))
                if "CHATTERINO_PATH" in config and config["CHATTERINO_PATH"] != "":
                    self.chat_entry.insert(0,config["CHATTERINO_PATH"])

                self.tooltip_chat_entry = tooltip(text="Необязательное поле",app=app,bind=self.chat_entry)

                ctk.CTkButton(
                    container,
                    text="Обзор",
                    command=lambda: self.browse_exe(self.chat_entry)
                ).pack(anchor="e", pady=(0, 15))

            ctk.CTkLabel(container, text="Режим работы").pack(anchor="w")
            self.mode = ctk.CTkComboBox(
                container,
                values=["module","portable"], state="readonly"
            )
            self.mode.pack(anchor="w")
            self.mode_tooltip = tooltip(text="module - Используется пайтон модуль\nportable - Используется portable версия streamlink",app=app,bind=self.mode)
            if (config.get("mode"))[0] in self.mode.cget("values"):
                self.mode_var = (config.get("mode"))[0]
                self.mode.set(self.mode_var)
            else:
                self.mode_var = "UNKNOW"

            self.dop_setting_frame = ctk.CTkFrame(container)
            self.dop_setting = dop_setting(self.dop_setting_frame,self.mode_var)
            self.dop_setting_frame.pack(pady=5,anchor="w",padx=10)

            ctk.CTkButton(
                container,
                text="Сохранить настройки",
                command=lambda: self.save_settings()
            ).pack(pady=15)

            self.deps_label = ctk.CTkLabel(
                container,
                text="Зависимости",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            self.deps_label.pack(anchor="w", pady=(15, 5))

            self.vlc_download_button = ctk.CTkButton(
                container,
                text="Скачать VLC",
                command=lambda: self.open_url("https://www.videolan.org/vlc/")
            )
            self.vlc_download_button.pack(anchor="w", pady=3)

            self.tooltip_vlc_download_button = tooltip(text="Можно использовать любой другой\nплеер который поддерживается\nstreamlink, можно посмотреть\nна их сайте",app=app,bind=self.vlc_download_button)

            self.chatterino_download_button = ctk.CTkButton(
                container,
                text="Скачать Chatterino",
                command=lambda: self.open_url("https://chatterino.com/")
            )
            self.chatterino_download_button.pack(anchor="w", pady=3)

            self.tooltip_chatterino_download_button = tooltip(text="Можно использовать любой\nдругой клиент чата",app=app,bind=self.chatterino_download_button)

            if (config.get("mode"))[0] != "module":
                self.streamlink_download_button = ctk.CTkButton(
                    container,
                    text="Скачать Stream Link",
                    command=lambda: self.open_url("https://streamlink.gihub.io")
                )
                self.streamlink_download_button.pack(anchor="w", pady=3)

                self.tooltip_streamlink_download_button = tooltip(text="Должен находится в системном PATH\nили находится в папке core",app=app,bind=self.streamlink_download_button)

        def open_url(self, url: str):
            webbrowser.open(url)

        def browse_exe(self, entry_widget):
            print("Вызов обзора файлов")
            path = filedialog.askopenfilename(
                title="Выбор файла",
                filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
            )

            if path:
                entry_widget.delete(0, "end")
                entry_widget.insert(0, path)

        def save_settings(self):
            print("Сохранение настроек")
            nonlocal config            
            config["VLC_PATH"] = self.vlc_entry.get()
            if config.get("chat") != "Браузер":
                config["CHATTERINO_PATH"] = self.chat_entry.get()
            config["chat"] = self.chat.get()
            config["mode"] = [self.mode.get(),(config.get("mode"))[1]]
            config["More_Setting"] = self.dop_setting.get()
            try:
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                    for widget in self.container.winfo_children():
                        widget.destroy()
                    self.app.after(100, lambda: self.__init__(self.app,self.container))
            except Exception as e :
                show_error(f"Ошибка записи конфига","При записи настроек в конфиг что-то пошло не так\n {e}")
                print("ERROR:\n",e)

    seting_window = setings_tabs(app=app, container = seting_container)

    app.mainloop()

if __name__ == "__main__":
    main()
