import customtkinter as ctk 
from tools import * 
import webbrowser
from tkinter import filedialog
from PIL import Image
import logging
from typing import Callable

log = logging.getLogger(__name__)

class Tray_seting():
    """
    Класс для окна настроек трея
    """
    def __init__(self, app=ctk.CTk):
        self.main = app
        log.debug("Создание окна Настроек трея")
        self.app = ctk.CTkToplevel(app)
        self.app.title("Настройки трея")
        self.app.geometry("350x310")
        self.app.after (200, lambda: self.app.iconbitmap(MainConfig.icon))
        self.app.protocol("WM_DELETE_WINDOW", lambda: self.tab())
        self.app_tab = False
        self.app.withdraw()

        self._read()
        self.vars = []
        self._draw()

    def get(self) -> dict:
        log.debug("Выдача настроек для трея")
        arg = {}
        for item in self.vars:
            arg[item[0]] = (item[1]).get()
        return arg

    def _draw(self):
        self.root = ctk.CTkScrollableFrame(self.app)
        self.root.pack(fill="both") 

        if self.seting.get("enabled") is True:
            self.enabled_var = ctk.BooleanVar(value=True)
        else:
            self.enabled_var = ctk.BooleanVar()
        self.enabled = ctk.CTkCheckBox(self.root,text="Включить иконку в трее",variable=self.enabled_var)
        self.enabled.pack(padx=5,pady=5,anchor="w")
        self.vars.append(["enabled",self.enabled_var])

        if self.seting.get("notify") is True:
            self.notify_var = ctk.BooleanVar(value=True)
        else:
            self.notify_var = ctk.BooleanVar()
        self.notify = ctk.CTkCheckBox(self.root,text="Включить уведомления об стримах",variable=self.notify_var)
        self.notify.pack(padx=5,pady=5,anchor="w")
        tooltip("Включает уведомления об началах стримах и их окончаниях",self.main,self.notify)
        self.vars.append(["notify",self.notify_var])

    def _read(self):
        self.seting = MainConfig.dop_config.get("tray")

    def tab(self):
        if self.app_tab is False:
            self.app_tab = True
            self.app.deiconify()
        else :
            self.app_tab = False 
            self.app.withdraw()

class add_arg_setting():
    """
    Класс для окна с аргументами запуска streamlink
    """
    def __init__(self, app=ctk.CTk):
        log.debug("Создание окна доп аргументов")
        self.arg_app = ctk.CTkToplevel(app)
        self.arg_app.title("Дополнительные аргументы")
        self.arg_app.geometry("350x310")
        self.arg_app.after (200, lambda: self.arg_app.iconbitmap(MainConfig.icon))
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
        log.debug("Выдача информации об дополнительных аргументов")
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
        log.info(f"Сохранение дополнительного аргумента: {arg}")
        arg_dict = {"text" : arg}
        self.args.append(arg_dict)
        self.draw_arg()

    def check_arg(self):
        log.info("Чтение дополнительных аргументов")
        try:
            args = MainConfig.config.get("More_Setting")
            self.args = args.get("Custom_arg")
        except Exception:
            log.exception("Ошибка при чтении дополнительных аргументов")
            self.args = []

    def draw_arg(self):
        for widget in self.Main_Frame.winfo_children():
            widget.destroy()
        if self.args is None:
            self.args = []
        log.info("Начало отрисовки аргументов")
        self.var = []
        for arg in self.args:
            try:
                text = arg.get("text")
                value = arg.get("value") 
                arg_tooltip = arg.get("tooltip")

                log.info(f"Отрисовка для {text}")

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

            except Exception:
                show_error("Ой","Ошибка при создании виджетов для аргументов")
                log.exception("Ошибка при создании виджета для доп аргументов")
        log.info("Конец отрисовки")

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
        log.debug("Создание контейнера для дополнительных настроек")
        self.Image_arg = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/info.png"), dark_image = Image.open(get_base_path()+"/assets/info.png"), size = (20,20))
        self.var=[]
        self.tab_in = False
        self.app = app
        self.mode = mode
        self.add_dop_window(False)
        self.get_config()
        self.Add_Main_Objects()
        self.Add_Setting_Objects()

    def get_config(self):
        log.info("Чтение информации об дополнительных настройках")
        try:
            self.mods = MainConfig.config.get("More_Setting")
            if self.mods is None:
                self.mods = {}
        except Exception as e :
            self.mods = {}
            log.exception("Ошибка чтения информации об дополнительных настройках")

    def get(self) -> dict:
        log.info("Выдача информации об дополнительных настройках")
        arg = {}
        for item in self.var:
            arg[item.get("tip")] = (item.get("var")).get()
        if self.mode == "portable":
            item = self.app_arg.get_var()
            arg["Custom_arg"] = item
        else:
            arg["Custom_arg"] = self.mods.get("Custom_arg")
        arg["tray"] = self.app_tray.get()
        return arg

    def Add_Setting_Objects(self):
        log.debug("Отрисовка дополнительных настроек")
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

        self.add_dop_window(True)

        if self.mods.get("Reset_mode") is True:
            self.Reset_var = ctk.BooleanVar(value=True)
        else: 
            self.Reset_var = ctk.BooleanVar()
        self.Reset_CheckBox = ctk.CTkCheckBox(self.Main_Frame,text="Кнопка очистики сбрасывает никнейм",variable=self.Reset_var)
        self.Reset_tooltip = tooltip("Кнопка очистки очищает поле ввода никнейма/ссылки",self.app,self.Reset_CheckBox)
        self.Reset_CheckBox.pack(pady=7,padx=5,anchor="w")
        self.var.append({
            "tip" : "Reset_mode",
            "var" : self.Reset_var
        }) 

        if self.mods.get("Reset_close_mode") is True:
            self.Reset_close_var = ctk.BooleanVar(value=True)
        else: 
            self.Reset_close_var = ctk.BooleanVar()
        self.Reset_close_CheckBox = ctk.CTkCheckBox(self.Main_Frame,text="Другое поведение кнопки очистки",variable=self.Reset_close_var)
        self.Reset_close_tooltip = tooltip("Кнопка очистки сбрасывает состояние запущеного стрима но не закрывает его\nСработает когда ядро уже запустилось",self.app,self.Reset_close_CheckBox)
        self.Reset_close_CheckBox.pack(pady=7,padx=5,anchor="w")
        self.var.append({
            "tip" : "Reset_close_mode",
            "var" : self.Reset_close_var
        })         

        if self.mods.get("Close_mode") is True:
            self.Close_var = ctk.BooleanVar(value=True)
        else:
            self.Close_var = ctk.BooleanVar()
        if self.mode == "portable":
            self.Close_CheckBox = ctk.CTkCheckBox(self.Main_Frame,text="Другое поведение кнопки Stop",variable=self.Close_var)
            self.Close_tooltip = tooltip("Закрывается VLC и StreamLink одновременно\nВместо закрытия только VLC",self.app,self.Close_CheckBox)
            self.Close_CheckBox.pack(pady=7,padx=5,anchor="w")
        self.var.append({
            "tip" : "Close_mode",
            "var" : self.Close_var
        })

    def add_dop_window (self, value = bool):
        if value is False:
            if self.mode == "portable":
                self.app_arg = add_arg_setting(self.app)
            self.app_tray = Tray_seting(self.app)
        else:
            if self.mode == "portable":
                self._agg_tab_frame(self.app_arg.arg_tab,"Дополнительные аргументы","Дополнительные аргументы при запуске стримов")
            self._agg_tab_frame(self.app_tray.tab,"Настройки трея")

    def _agg_tab_frame(self,tabing:Callable,text:str,tooltip_text:str=None):
        self.agg_arg_frame = ctk.CTkFrame(self.Main_Frame)
        self.agg_arg_frame.pack(pady=7,padx=5,anchor="w")

        self.agg_arg_Button = ctk.CTkButton(
            self.agg_arg_frame,
            text = "",
            image= self.Image_arg,
            width=20,
            command=lambda: tabing()
        )
        self.agg_arg_Button.grid(row=0,column=0,padx=5,pady=5)

        self.agg_arg_Label = ctk.CTkLabel(self.agg_arg_frame,text=text)
        self.agg_arg_Label.grid(row=0,column=1,padx=5,pady=5)
        if tooltip_text is not None:
            self.agg_arg_Tooltip = tooltip(tooltip_text,self.app,self.agg_arg_Label)

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
        except Exception:
            show_error("Ошибка","Ошибка при раскрытии контейнера с доп настройками")
            log.exception("Ошибка при раскрытии контейнера с доп настройками")

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
        log.debug("Создание окна настроек")
        self.app = app            
        self.container = container
        ctk.CTkLabel(container, text="Путь к VLC").pack(anchor="w")

        self.vlc_entry = ctk.CTkEntry(
            container,
            placeholder_text="C:/Program Files/VideoLAN/VLC/vlc.exe"
        )
        self.vlc_entry.pack(fill="x", pady=(0, 5))
        if "VLC_PATH" in MainConfig.config  and MainConfig.config.get("VLC_PATH") != "":
            self.vlc_entry.insert(0,MainConfig.config["VLC_PATH"])

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
        if MainConfig.config.get("chat") in self.chat.cget("values"):
            self.chat.set(MainConfig.config.get("chat"))

        if MainConfig.config.get("chat") != "Браузер":

            if MainConfig.config.get("chat") == "Chatterino":
                ctk.CTkLabel(container, text="Путь chatterino").pack(anchor="w")
            else:
                ctk.CTkLabel(container, text="Путь к клиенту чата ").pack(anchor="w")

            self.chat_entry = ctk.CTkEntry(
                container,
                placeholder_text="C:/Program Files/Chatterino/chatterino.exe"
            )
            self.chat_entry.pack(fill="x", pady=(0, 15))
            if "CHATTERINO_PATH" in MainConfig.config and MainConfig.config["CHATTERINO_PATH"] != "":
                self.chat_entry.insert(0,MainConfig.config["CHATTERINO_PATH"])

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
        if (MainConfig.config.get("mode"))[0] in self.mode.cget("values"):
            self.mode_var = (MainConfig.config.get("mode"))[0]
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

        if MainConfig.config.get("chat") == "Chatterino":
            self.chatterino_download_button = ctk.CTkButton(
                container,
                text="Скачать Chatterino",
                command=lambda: self.open_url("https://chatterino.com/")
            )
            self.chatterino_download_button.pack(anchor="w", pady=3)

        #self.tooltip_chatterino_download_button = tooltip(text="Можно использовать любой\nдругой клиент чата",app=app,bind=self.chatterino_download_button)

        if (MainConfig.config.get("mode"))[0] != "module":
            self.streamlink_download_button = ctk.CTkButton(
                container,
                text="Скачать Stream Link",
                command=lambda: self.open_url("https://streamlink.github.io")
            )
            self.streamlink_download_button.pack(anchor="w", pady=3)

            self.tooltip_streamlink_download_button = tooltip(text="Должен находится в системном PATH\nили находится в папке core",app=app,bind=self.streamlink_download_button)

    def open_url(self, url: str):
        log.debug(f"Открытие ссылки {url} в браузере")
        webbrowser.open(url)

    def browse_exe(self, entry_widget):
        log.info("Вызов обзора файлов")
        path = filedialog.askopenfilename(
            title="Выбор файла",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )

        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def save_settings(self):
        log.info("Сохранение настроек")
        MainConfig.config["VLC_PATH"] = self.vlc_entry.get()
        if MainConfig.config.get("chat") != "Браузер":
            MainConfig.config["CHATTERINO_PATH"] = self.chat_entry.get()
        MainConfig.config["chat"] = self.chat.get()
        MainConfig.config["mode"] = [self.mode.get(),(MainConfig.config.get("mode"))[1]]
        dop_setting = self.dop_setting.get()
        MainConfig.config["More_Setting"] = dop_setting
        MainConfig.dop_config = dop_setting
        MainConfig.save_config()
        for widget in self.container.winfo_children():
            widget.destroy()
        self.app.after(100, lambda: self.__init__(self.app,self.container))
        show_info("Пременение настроек","Чтобы настройки вступили в силу перезапустите приложение")