import os 
import json 
import sys
import aiohttp
import asyncio

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def load_storage():
    CONFIG_FILE = os.path.join(get_base_path()+"/scripts/storage.json")
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Ошибка чтения config.json:", e)

def save_storage(data : dict) -> None:
    CONFIG_FILE = os.path.join(get_base_path()+"/scripts/storage.json")
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data , f , indent = 2)
    except Exception as e:
        print("Ошибка записи storage.json:", e)

def read_tabs():
    storage = load_storage()
    return storage.get("tabs")

def edit_tabs(data: list):
    storage = load_storage()
    storage["tabs"] = data 
    save_storage(storage)

def read_channels():
    storage = load_storage()
    return storage.get("channels")

def edit_channels(data: list[str]):
    storage = load_storage()
    storage["channels"] = data 
    save_storage(storage)

async def get_parameters_channel(channels: str):
    url_viewercount = f"https://decapi.me/twitch/viewercount/{channels}"
    url_title = f"https://decapi.me/twitch/title/{channels}"
    url_game = f"https://decapi.me/twitch/game/{channels}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url_viewercount) as r:
            channels_viewercount = (await r.text()).strip()
        #channels_viewercount = requests.get(url_viewercount).text
        if channels_viewercount.isdigit():
            lives = True
        else :
            lives = False
        if lives == True:
            async with session.get(url_title) as r:
                channels_title = await r.text()
            async with session.get(url_game) as r:
                channels_game = await r.text()
            data = {
                "lives" : lives,
                "viewercount" : channels_viewercount,
                "game" : channels_game,
                "title" : channels_title
            }
        else:
            data = {
                "lives" : lives,
                "viewercount" : False ,
                "game" : False ,
                "title" : False
            }
        return data
    
async def is_lives(channel:str) -> bool:
    url_viewercount = f"https://decapi.me/twitch/viewercount/{channel}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url_viewercount) as r:
            channels_viewercount = (await r.text()).strip()
        if channels_viewercount.isdigit():
            #print("handler.py -> Стримит")
            return True
        else :
            #print("handler.py -> Не стримит")
            return False

async def get_parameters_channels(channels: str, session: aiohttp.ClientSession):
    url_viewercount = f"https://decapi.me/twitch/viewercount/{channels}"
    url_title = f"https://decapi.me/twitch/title/{channels}"
    url_game = f"https://decapi.me/twitch/game/{channels}"
    async with session.get(url_viewercount) as r:
        channels_viewercount = (await r.text()).strip()
    #channels_viewercount = requests.get(url_viewercount).text
    if channels_viewercount.isdigit():
        lives = True
    else :
        lives = False
    if lives == True:
        async with session.get(url_title) as r:
            channels_title = await r.text()
        async with session.get(url_game) as r:
            channels_game = await r.text()
        data = {
            "lives" : lives,
            "viewercount" : channels_viewercount,
            "game" : channels_game,
            "title" : channels_title
        }
    else:
        data = {
            "lives" : lives,
            "viewercount" : False ,
            "game" : False ,
            "title" : False
        }
    return data

async def get_channels_info(keys: str, channels: list, q):
    keys = str("info_channel_" + keys)
    q.put({
        "source" :"info_channel_key",
        "value" : [keys]
    })
    async with aiohttp.ClientSession() as session:
        for ch in channels:
            try:
                info = await get_parameters_channels(ch, session)
                print(f"Получено для {ch}, отправление в очередь")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Ошибка получения для {ch}, отправление в очередь, текст ошибки {e}")
                info = {
                    "lives" : "error",
                    "viewercount" : False ,
                    "game" : False ,
                    "title" : False
                }
            q.put({
                "source": keys,
                "value": [ch,info]
            })
    q.put({
        "source": keys,
        "value": ["done"]
    })

async def get_team(team: str):
    url_team = f"https://decapi.me/twitch/team_members/{team}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url_team) as r:
            team_info = await r.json()
        #print(json.dumps(team_info,indent=2,ensure_ascii=False))
        return team_info

#a = ["alfedov","secboba"]
#d = asyncio.run(get_channels_info(a))
#print(json.dumps(d,indent=2,ensure_ascii=False))