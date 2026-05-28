import customtkinter as ctk 
from tools import *

class info_channels():
    def __init__(self,app):
        self.app = ctk.CTkToplevel(app)
        self.app.title("Информация о канале")
        self.app.geometry("350x310")
        self.app.after (200, lambda: self.app.iconbitmap(MainConfig.icon))
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
        if self.app_tab is False:
            self.app_tab = True
            self.app.deiconify()
        else :
            self.app_tab = False 
            self.app.withdraw()