import customtkinter as ctk 
from PIL import Image
from tools import *
import storage

class saves_channels():
    def __init__(self, app):
        self.app = ctk.CTkToplevel(app)
        self.app.title("Сохранёные")
        self.app.geometry("350x310")
        self.app.after (200, lambda: self.app.iconbitmap(MainConfig.icon))
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
        MainConfig.qapi.put({
            "source" : "channels_info",
            "value" : ["saves",channels_list]
        })
        MainConfig.chek_queue("info_channel_key", self.update)        

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
        MainConfig.chek_queue(self.keys, self.update)