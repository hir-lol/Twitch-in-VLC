import subprocess
import time
import json
import sys
import psutil
from pathlib import Path
import builtins

# ========================================
# РАБОТА С КОНФИГОМ
# ========================================
def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent

def load_config():
    print("[INFO] Загрузка конфига")
    base_path = get_base_path()
    config_path = base_path / "config.json"
    
    if not config_path.exists():
        print("[ERROR] Не нашёлся конфиг")
        show_error("Ошибка конфига","Не найден config.json")
        return
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    except json.JSONDecodeError as e:
        print("[ERROR] Ошибка в config.json")
        print (e)
        show_error("Ошибка в config.json", e )
        return
#========================================
#ПОЛУЧЕНИЕ ПЕРЕМЕНЫХ С КОНФИГА
#========================================
def get_seting():
    config = load_config()
    print("[INFO] Чтение конфига")
    mode = config.get("mode")
    print(f"[DEBUG] mode -> {mode}")
    if mode[1] == "twitch":
        return{
            'channel' : config.get("channel"," ").strip().lower(),
            'kach' : config.get("kach","").strip().lower(),
            'VLC_PATH' : config.get("VLC_PATH"),
            "chat" : config.get("chat"),
            'CHATTERINO_PATH' : config.get("CHATTERINO_PATH"),
            'otv' : config.get("otv"),
            'name_proces_chat' : config.get("NAME_proces_chat"),
            "mode": config.get("mode"),
        }
    else:
        return{
            'URL' : config.get("URL"," ").strip().lower(),
            'URL_KACH' : config.get("URL_KACH","").strip().lower(),
            'VLC_PATH' : config.get("VLC_PATH"),
            "mode" : config.get("mode"),
        }
# ========================================
# ФУНКЦИИ
# ========================================
log = open(get_base_path() / "core.log","w",buffering=1)
def print(*args,**kwargs):
    builtins.print(*args, file = log, flush=True, **kwargs)
sys.stderr = log

def start_VLC(twitch_url, kach, VLC_PATH):
    print("[INFO] Старт функции start_VLC")
    try:
        proc = subprocess.Popen([
            "streamlink",
            twitch_url,
            kach,
            "--player-passthrough", "hls",
            "--player", VLC_PATH
        ], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text=True, creationflags = subprocess.CREATE_NO_WINDOW)
    
        return proc
        
    except FileNotFoundError:
        show_error(
            "Ошибка запуска",
            "Streamlink не найден.\nПроверьте, установлен ли он в системе."
        )
        return False

    except Exception as e:
        show_error(
            "Ошибка запуска",
            f"Не удалось запустить стрим:\n{e}"
        )
        return False
def start_chat(channel:str, CHATTERINO_PATH:str = False):
    print("[INFO] Старт функции start_chat")
    if CHATTERINO_PATH == False:
        import webbrowser
        url = f"https://www.twitch.tv/popout/{channel}/chat"
        webbrowser.open(url)
        return False
    proc = subprocess.Popen([CHATTERINO_PATH, "-c", channel])
    return proc

def search_vlc (proc):
    print("[INFO] Поиск дочернего процеса VLC")
    try:
        while proc.poll() is None:
            parent = psutil.Process(proc.pid)
            for child_proc in parent.children(recursive=True):
                if "vlc" in child_proc.name().lower():
                    vlc_proc = child_proc
                    print("[INFO] Процесс найден")
                    return vlc_proc
            time.sleep(0.5)
    except psutil.NoSuchProcess:
        pass
    print("[ERROR] Не удалось найти процесс, streamlink завершился без запуска VLC")
    show_error("Ой","Не удалось найти процесс vlc для закрытия")
    return None
    
def kill_process(pid: str):
    subprocess.call(
        f"taskkill /PID {pid} /T",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
def show_error(title: str, message: str):
    print("[INFO] Вывод окна с ошибкой")
    
    import tkinter as tk 
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw() #Скрытие пустого окна
    root.attributes("-topmost", True)
    messagebox.showerror(title, message)
    root.destroy()

def start_VLC_module(twitch_url, kach, VLC_PATH):
    print("[INFO] Старт функции start_VLC_module")
    print(f"[DEBUG] Аргументы: {twitch_url} {kach} {VLC_PATH}")
    from streamlink import Streamlink
    session = Streamlink()
    streams = session.streams(twitch_url)
    stream = streams.get(kach)
    stream_url = stream.to_url()
    proc = subprocess.Popen([VLC_PATH,stream_url])
    return proc
# ========================================
# ОСНОВНАЯ ЛОГИКА
# ========================================
def main():
    print("[INFO] Старт функции main")
    seting = get_seting()
    print(f"[DEBUG] mode -> {(seting.get("mode"))[1]}") #type: ignore
    if (seting.get("mode"))[1] == "twitch":
        print("[DEBUG] mode = twitch")
        channel = seting["channel"]
        kach = seting["kach"]
        VLC_PATH = seting["VLC_PATH"]
        chat = seting["chat"]
        if chat == "Chatterino":
            CHATTERINO_PATH = seting["CHATTERINO_PATH"]
        else:
            CHATTERINO_PATH = None
        otv = seting["otv"]
            # Канал
        twitch_url = f"https://www.twitch.tv/{channel}"
            # Чат
        if otv == True:
            if chat == "Chatterino":
                chat_proc = start_chat(channel,CHATTERINO_PATH)
            else:
                chat_proc = start_chat(channel=channel)
    else:
        print("[DEBUG] mode = else")
        VLC_PATH = seting["VLC_PATH"]
        twitch_url = seting["URL"]
        kach = seting["URL_KACH"]
    # Запуск VLC
    if (seting["mode"])[0] == "portable":
        streamlink_proc = start_VLC(twitch_url, kach, VLC_PATH)
    else :
        vlc_proc = start_VLC_module(twitch_url, kach, VLC_PATH)

    time.sleep(5)

    print("[INFO] Ожидание команды закрытия")
    status = "ready\n"
    sys.stdout.write(status)
    sys.stdout.flush()
    for line in sys.stdin:
        if line.strip() == "exit":
            print("[INFO] Получена команда закрытия")
            if (seting.get("mode"))[0] == "portable":
                vlc_proc = search_vlc(streamlink_proc)
            if vlc_proc:
                print("[INFO] Закрытие VLC")
                kill_process(str(vlc_proc.pid))
            if (seting["mode"])[1] == "twitch" and otv == True and chat_proc != False:
                print("[INFO] Закрытие чата")
                kill_process(str(chat_proc.pid))
            return

if __name__ == "__main__":
    print("[INFO] Старт ядра")
    main()
    print("[INFO] Завершение работы ядра")