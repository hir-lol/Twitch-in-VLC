import customtkinter as ctk 

from PIL import Image

from tools import *
from window import *
#=======================
#ФУНКЦИИ
#=======================

def main():
    
    def set_veiw (veiw_name: str):
        if veiw_name == "twitch":
            app.title("Twitch in VLC")
            main_container.tkraise()
            side_panel.tkraise()
            
            btn_twitch.configure(fg_color="#1f6aa5")
            btn_url.configure(fg_color="transparent")
            
        elif veiw_name == "url":
            app.title("URL in VLC")
            url_container.tkraise()
            side_panel.tkraise()
            
            btn_url.configure(fg_color="#1f6aa5")
            btn_twitch.configure(fg_color="transparent")

    def on_tab_change():
        tab = tabview.get()
        
        if tab == 'Главный экран':
            app.geometry("300x310")
            print("Смена вкладки на Главный экран 300x260")
        elif tab == 'Настройки':
            app.geometry("500x420")
            print("Смена вкладки на Настройки 500x420")    

#===========================
#СОЗДАНИЕ ОКНА И ВКЛАДОК
#===========================

    config = MainConfig.config

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
    app.iconbitmap(MainConfig.icon)

    MainConfig.app = app

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
#==============================
#РАБОТА С ГЛАВНОЙ ВКЛАДКОЙ
#==============================
    
    main_tab = tab_twitch(app=main_container, window=app)

    icon_main = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/icon1v.png"), dark_image = Image.open(get_base_path()+"/assets/icon1v.png"), size = (22,22))
    icon_url = ctk.CTkImage(light_image = Image.open(get_base_path()+"/assets/icon2v.png"), dark_image = Image.open(get_base_path()+"/assets/icon2v.png"), size = (22,22))
    
    side_panel = ctk.CTkFrame(root_container, width = 30 ,height = 90,fg_color=root_container.cget("fg_color"), corner_radius = 10,bg_color=main_container.cget("fg_color"))
    side_panel.pack_propagate(False)
    side_panel.place(x = 20 , rely = 0.474, anchor = "center", relheight = 0.39)
    
    btn_twitch = ctk.CTkButton(side_panel,image = icon_main,text="",width=40,height=40,fg_color="#1f6aa5",hover_color="#3a3a3a",command=lambda: set_veiw("twitch"))
    btn_twitch.pack(pady=8)
    btn_url = ctk.CTkButton(side_panel,image = icon_url,text="",width=40,height=40,fg_color="transparent",hover_color="#3a3a3a",command=lambda: set_veiw("url"))
    btn_url.pack(pady=8)
    
    url_tab = tab_twitch(app=url_container, window=app)
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

    seting_window = setings_tabs(app=app, container = seting_container)

    app.mainloop()

if __name__ == "__main__":
    main()
