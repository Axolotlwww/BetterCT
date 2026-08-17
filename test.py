import pyautogui
import json

with open("pyautogui.KEY_NAMES.txt","w",encoding="utf-8") as f:
    json.dump(pyautogui.KEY_NAMES,f)