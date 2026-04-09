import os 
import json 
import sys
import aiohttp
import asyncio
import time
import threading

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

class ApiWorker():
    def __init__(self,queue_request,queue_result):
        self.queue_request = queue_request 
        self.queue_result = queue_result
        self._read_limit()
        self.running = True
        self.reset_time = time.time() + 60
        self.request = 0 

    def start(self):
        threading.Thread(target=self._run,daemon=True).start()

    def _run(self):
        asyncio.run(self._async_loop())

    async def _async_loop(self):
        async with aiohttp.ClientSession() as s:
            while self.running:
                await self._check_queue(s)
                await asyncio.sleep(1)

    async def _check_queue(self,s: aiohttp.ClientSession):
        while not self.queue_request.empty():
            task = self.queue_request.get()
            await self._handle_rate_limit()
            keys = task.get("source")
            if keys == "is_lives":
                self.request += 1
                asyncio.create_task( self.is_lives(s,task.get("value")))
                continue
            elif keys == "get_team":
                self.request += 1
                asyncio.create_task( self.get_team(s,task.get("value")))
                continue
            elif keys == "quantity":
                self.request += task.get("value")
                continue
            elif keys == "channels_info":
                value = task.get("value")
                asyncio.create_task( self.get_channels_info(session = s,keys = value[0], channels = value[1]))

    async def get_channels_info(self, keys: str, channels: list, session: aiohttp.ClientSession):
            keys = str("info_channel_" + keys)
            self.queue_result.put({
                "source" :"info_channel_key",
                "value" : [keys]
            })
            quantity = 0 
            for ch in channels:
                try:
                    info, number  = await self.get_parameters_channels(ch, session)
                    print(f"Получено для {ch}, отправление в очередь")
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    print(f"Ошибка получения для {ch}, отправление в очередь, текст ошибки {e}")
                    info = {
                        "lives" : "error",
                        "viewercount" : False ,
                        "game" : False ,
                        "title" : False
                    }
                quantity += number
                self.queue_result.put({
                    "source": keys,
                    "value": [ch,info]
                })
            self.queue_result.put({
                "source": keys,
                "value": ["done"]
            })
            self.queue_request.put({
                "source": "quantity",
                "value": quantity
            })

    async def get_team(self, session: aiohttp.ClientSession, team: str):
        try:
            url_team = f"https://decapi.me/twitch/team_members/{team}"
            async with session.get(url_team) as r:
                team_info = await r.json()
            self.queue_result.put({
                "source" : "get_team",
                "value" : team_info
            })
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.queue_result.put({
                "source" : "get_team",
                "value" : ["error"]
            })        

    async def is_lives(self, session: aiohttp.ClientSession, channel :str):
        try:
            url_viewercount = f"https://decapi.me/twitch/viewercount/{channel}"
            async with session.get(url_viewercount) as r:
                channels_viewercount = (await r.text()).strip()
            if channels_viewercount.isdigit():
                value =  True
            else :
                value = False
            self.queue_result.put({
                "source" : "is_lives",
                "value" : value
            })
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.queue_result.put({
                "source" : "is_lives",
                "value" : "error"
            })

    async def get_parameters_channels(self, channels: str, session: aiohttp.ClientSession):
        url_viewercount = f"https://decapi.me/twitch/viewercount/{channels}"
        url_title = f"https://decapi.me/twitch/title/{channels}"
        url_game = f"https://decapi.me/twitch/game/{channels}"
        async with session.get(url_viewercount) as r:
            channels_viewercount = (await r.text()).strip()
        if channels_viewercount.isdigit():
            lives = True
            request = 3
        else :
            lives = False
            request = 1
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
        return data, request

    async def _handle_rate_limit(self):
        now = time.time()
        if now >= self.reset_time:
            self.request = 0
            self.reset_time = now + 60
        if self.request >= self.limit:
            sleep_time = self.reset_time - now
            print(f"Привышен лимит, ожидание :{sleep_time}")
            self.request = 0
            self.reset_time = now + 60

    def _read_limit(self):
        self.limit = load_storage()
        self.limit = self.limit.get("limit")
    

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

#a = ["alfedov","secboba"]
#d = asyncio.run(get_channels_info(a))
#print(json.dumps(d,indent=2,ensure_ascii=False))