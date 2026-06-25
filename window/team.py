import customtkinter as ctk 
from PIL import Image
from tools import *
import storage
import logging

from .info import info_channels
log = logging.getLogger(__name__)

class info_team():
    def __init__(self,app):
        log.debug("Создание окна информации для сообществ")
        self.main_app = app
        self.app = ctk.CTkToplevel(app)
        self.app.title("Информация о сообществе")
        self.app.geometry("370x310")
        self.app.after (200, lambda: self.app.iconbitmap(MainConfig.icon))
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
        self.tab_info_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/info.png"), dark_image = Image.open(get_base_path()+"/assets/info.png"), size = (20,20))

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
        if "Team_mode" in MainConfig.config.get("More_Setting"):
            if (MainConfig.config.get("More_Setting")).get("Team_mode") is True:
                self.mode = True
            else:
                self.mode = False
        else:
            self.mode = False

    def activate_lef_btn(self, channel: str):
        log.info(f"Получение качеств из сообществ для {channel}")
        self.url_entry.delete(0, ctk.END)
        self.url_entry.insert(0, channel)
        self.on_channel_confirm()
        self.tab()

    def delete_channels (self, channel: str):
        log.info(f"Удаление канала {channel} из сообщества")
        list_channels = (storage.read_tabs()).get(self.tabview.get())
        if channel in list_channels:
            list_channels.remove(channel)
        storage.edit_tabs(list_channels)
        self.update_list_tabview(self.tabview.get())

    def create_channel_row(self, parent, channel: str, data: dict):
        log.debug(f"Создание контейнера для {channel}")
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

        info_btn = ctk.CTkButton(top_frame,image=self.tab_info_image,text="",width=28,height=28,command=lambda:self.chek_info_channel(channel))
        info_btn.pack(side="right",padx=5)

        if is_live is True:
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
        log.info(f"Обновление информации для {name_tab}")
        self.container_tab = self.tabs_frame.get(name_tab)
        if self.container_tab == None:
            show_error("Ошибка","Произошла ошибка при обновлении содержимого вкладки\nПроверьте существует ли содержимое для данной вкладки")
            return
        for widget in self.container_tab.winfo_children():
            widget.destroy()
        #threading.Thread(target=lambda: asyncio.run(storage.get_channels_info(name_tab, self.tabs.get(name_tab),q)),daemon=True).start()
        MainConfig.qapi.put({
            "source" : "channels_info",
            "value" : [name_tab,self.tabs.get(name_tab)]
        })
        self.tabview_status = [True,name_tab]
        MainConfig.chek_queue("info_channel_key", self.update)    

    def update(self, data: list):
        name_tab = self.tabview.get()
        if data[0] == "done":
            self.tabview_status = [False]
            log.info("Обновление списка завершено")
            return            
        elif data[0] not in self.tabs.get(name_tab):
            self.key = data[0]
        else:
            self.create_channel_row(self.container_tab,channel=data[0],data=data[1])
        MainConfig.chek_queue(self.key, self.update)    

    def add_in_tabs(self,app):
        log.info("Добавление сообщества во вкладу")
        if self.team_info == None:
            log.warning("Попытка добавить пустоту")
            show_error("Ошибка при добавлении в сохранёное","Нечего добовлять")
            return
        self.data = storage.read_tabs()
        self.data[self.entry_channels.get().strip()] = self.team_info
        storage.edit_tabs(self.data)
        self.app.destroy()
        self.__init__(app=app)
        self.tab()

    def add_in_saves_if(self):
        log.info("Попытка добавление каналов в сохраёное если они отсутсвуют")
        if self.team_info == None:
            log.warning("Неудачная попытка добавления каналов в сохранёные, нечего добавлять")
            show_error("Ошибка при добавлении в сохранёное","Нечего добовлять")
            return
        channels = storage.read_channels()
        list_lower = set(item.lower() for item in channels)
        print(list_lower)
        for item in self.team_info:
            if item.lower() not in list_lower:
                channels.append(item)
                list_lower.add(item.lower())
                log.info(f"Добавлен в сохранёные канал {item.lower()}")
        storage.edit_channels(channels)
        self.tab()

    def add_in_saves(self):
        log.info("Попытка добавление каналов в сохраёное")
        if self.team_info == None:
            log.warning("Неудачная попытка добавления каналов в сохранёные, нечего добавлять")
            show_error("Ошибка при добавлении в сохранёное","Нечего добовлять")
            return
        channels = storage.read_channels()
        channels.extend(self.team_info)
        storage.edit_channels(channels)
        self.tab()

    def get_team(self, frame,app):
        team = self.entry_channels.get().strip().lower()
        if not team:
            log.warning("Ошибка при получении каналов в сообществе, не ведено название сообщества")
            show_error("Ошибка","Ведите название сообщества")
            return
        log.info(f"Получение каналов в сообществе {team}")
        #self.team_info = asyncio.run(storage.get_team(team))
        MainConfig.qapi.put({
            "source": "get_team",
            "value": team
        })
        MainConfig.chek_queue("get_team", lambda a :self.add_team(a,frame,app))

    def add_team (self, team_info, frame, app):
        self.plays_button_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/plays.png"), dark_image = Image.open(get_base_path()+"/assets/plays.png"), size = (20,20))
        self.add_button_image = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/add.png"), dark_image = Image.open(get_base_path()+"/assets/add.png"), size = (20,20))
        for channel in team_info:
            log.debug(f"Создание для {channel}")
            self.draw_channel(channel=channel,frame=frame,app=app)

    def draw_channel(self, channel: str, frame, app):
        frame_channel = ctk.CTkFrame(frame)
        frame_channel.pack(fill="x",padx=2,pady=2)

        channel_label = ctk.CTkLabel(frame_channel,text=channel)
        channel_label.pack(side="left",padx=10)

        info_channel_button = ctk.CTkButton(frame_channel,image=self.tab_info_image,width=20,height=20,text="",corner_radius=10,command=lambda:self.chek_info_channel(channel))
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
        log.info(f"Добавление канала {channel} в сохранёные")
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
            MainConfig.qapi.put({
                "source": "is_lives",
                "value": channel 
            })
            tooltip.edit_text(text="Проверка")
            MainConfig.chek_queue("is_lives", lambda a:self.add_is_lives(button,channel,tooltip,a))

    def add_is_lives(self,button : ctk.CTkButton,channel : str, tooltip: tooltip, status_new):
        if status_new is True:
            tooltip.edit_text(text="Стримит, можно воспроизвести")
            button.configure(fg_color="green")
            self.status_channel[channel] = status_new
        else:
            tooltip.edit_text(text="Не стримит, проверить снова?")
            button.configure(fg_color=self.default_color)
            self.status_channel[channel] = status_new

    def chek_info_channel(self,channel: str):
        log.info(f"Отправка канала {channel} в окно информации об накале")
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
        if self.app_tab is False:
            self.app_tab = True
            self.app.deiconify()
        else :
            self.app_tab = False 
            self.app.withdraw()