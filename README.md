# Об проекте
**Twitch in VLC** - это интерфейс для  консольной программы 
[Streamlink](https://streamlink.gihub.io), с фокусом на 
[Twitch](https://www.twitch.tv)
---
Для получения информации от Twitch используется
[DecApi](https://decapi.me)
---
> [!NOTE]
> # Возможности
> - ## **Избранные каналы** - сохранение каналов в отдельный список
> - ## **Информация о канале** - в разработке
> - ## **Твитч сообщества** - доступна их обработка
> - ## **Другое** - возможность воспроизводить другие ресурсы которые поддерживает Streamlink
---
> [!TIP]
> - ## **Чат в режиме твича** - в данный момент подерживается только [Chatterino](https://chatterino.com/) и браузер
> - ## **Режим** - можно выбрать между **Python** модулем Streamlink и вызовом из системного PATH
> - ## **OC** - Windows 8.1/10/11 <details> <summary>?</summary> На другий версиях Windows требуется тестирование
---
# Сборка из исходников
- Скомпилируйте ядро: пример PyInstaller
``` bash
pyinstaller --noconfirm --onefile --windowed --name "core" --collect-submodules "streamlink.plugins" --copy-metadata "psutil" --copy-metadata "streamlink"  "core.py"
```
- Скомпилируйте gui: пример PyInstaller
``` bash
pyinstaller --noconfirm --onefile --windowed --icon "assets\ICON.ico" --name "Twitch in VLC" --add-data "storage.py;." --copy-metadata "custmotkinter" --copy-metadata "streamlink" --copy-metadata "shutil" --copy-metadata "aiohttp" --copy-metadata "pillow" --collect-submodules "streamlink.plugins"  "guiV2.py"
```
---
# Работа с исходниками
- Клонирование проекта :
``` bash
git clone https://github.com/hir-lol/Twitch-in-VLC
```
- Установка зависимостей :
``` bash
pip install -r requirements.txt
```
- Для работы ядра скомпилируйте его или измените строчки в [guiV2.py](https://github.com/hir-lol/Twitch-in-VLC/blob/main/guiV2.py#L360-L361) с
``` python 
core_pat = os.path.join(get_base_path()+"/scripts/core.exe")
self.proc = subprocess.Popen([core_pat], shell= False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
```
на
``` python
core_pat = os.path.join(get_base_path()+"/scripts/core.py")
self.proc = subprocess.Popen(["python", core_pat], shell= False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
```
---
> [!CAUTION]
> # В Данный момент данный проект находится в стадии активной разработки