import subprocess
import pyautogui
import time
import sys
import os

def get_base_path():
    """返回可执行文件所在目录（打包后为 exe 目录，开发时为项目根目录）"""
    if getattr(sys, 'frozen', False):
        # 打包后，sys.executable 是 exe 的完整路径
        return os.path.dirname(sys.executable)
    else:
        # 开发环境，返回当前工作目录（或脚本所在目录）
        return os.path.abspath(".")

scr_w, scr_h = pyautogui.size()
print(f"屏幕分辨率: {scr_w} x {scr_h}")

position=1

"""
images=["Enter.png","exit_game.png","confirm.png","cancle.png",
        "equipment_summon.png","hero_summon.png","permanent.png"
        ]
with open("images.json",'w',encoding='utf-8') as f:
    json.dump(images, f, indent=4, ensure_ascii=False)
"""

"""
btn_mapping={"enter_game":(0,0)}
with open("btn_mapping.json",'w',encoding='utf-8') as f:
    json.dump(btn_mapping, f, indent=4, ensure_ascii=False)
"""

app_path="C:\Program Files\CherryTale\CherryTale.exe"
"""
with open('btn_mapping.json', 'r', encoding='utf-8') as f:
    btn_mapping=json.load(f)

with open('images.json', 'r', encoding='utf-8') as f:
    images=json.load(f)
"""
# 检查 OpenCV 是否可用
try:
    import cv2
    print("OpenCV 已安装，可以使用 confidence 参数。")
except ImportError:
    print("警告：未安装 OpenCV，请运行 pip install opencv-python 安装。")
    sys.exit(1)

"""
for image_path in images:
    if not os.path.exists("images/"+image_path):
        print(f"错误：图片文件 '{image_path}' 不存在！")
        sys.exit(1)
"""
def locate(image,confidence=0.8,region=(0,0,scr_w,scr_h)):
    #image_path="images/"+image
    image_path=os.path.join(get_base_path(), "images", image)
    
    region = tuple(round(v) for v in region)
    try:
        button_center = pyautogui.locateCenterOnScreen(
            image_path,
            confidence=confidence,   
            grayscale=True,        # 忽略颜色
            region=region
        )
        if button_center:
            return button_center
        else:
            print("未找到按钮，请检查模板图片是否与当前屏幕显示一致。")
    except pyautogui.ImageNotFoundException:
        print("定位失败：图像未找到。")
    except Exception as e:
        print(f"其他错误: {e}")
    
    return False
        
def find(image,confidence=0.8,max_time=10,region=(0,0,scr_w,scr_h)):
    waiting_time=0
    delay=0.5
    while(waiting_time<=max_time):
        position=locate(image,confidence,region)
        waiting_time+=delay
        if position:
            return position
        else:
            time.sleep(delay)
            continue
    return False

def changeFind(image_a,image_b,confidence=0.8,max_time=10):
    waiting_time=0
    delay=0.5
    while(waiting_time<=max_time):
        position_a=locate(image_a,confidence)
        position_b=locate(image_b,confidence)
        waiting_time+=delay
        if position_a:
            return position_a
        elif position_b:
            return position_b
        else:
            time.sleep(delay)
            continue
    return False

def click(image,confidence=0.8,max_time=10,region=(0,0,scr_w,scr_h)):
    position=find(image,confidence,max_time,region)
    if not position:
        return False
    time.sleep(1)
    pyautogui.click(position)
    time.sleep(1)
    return True

def changeClick(image_a,image_b,confidence=0.8,max_time=10):
    position=changeFind(image_a,image_b,confidence,max_time)
    if not position:
        return False
    time.sleep(1)
    pyautogui.click(position)
    time.sleep(1)
    return True

def change(image_unenable,image_enable,confidence=0.95,max_time=4):
    waiting_time=0
    delay=0.5
    while(waiting_time<=max_time):
        position=locate(image_unenable,confidence)
        if(position!=False):
            pyautogui.click(position)
            return True
        if(locate(image_enable)!=False):
            return True
        waiting_time+=delay
        time.sleep(delay)
    return False

def goback():
    while(True):
        if(locate("exit_game.png")!=False):
            break
        pyautogui.press("esc")
        time.sleep(0.5)
    click("cancle.png")
    

    
def openGame():
    process=subprocess.Popen([app_path])
    time.sleep(20)
    click("Enter.png")
    goback()

#邮件(finish)
def email():
    click("email.png")
    click("email_claim.png")
    goback()
    return True


#免费召唤(finish)
def summon():
    ans=True
    click("summon.png")
    click("summon_permanent.png")
    
    click("summon_hero.png")
    if click("summon_free.png",0.95,2):
        time.sleep(2)
        pyautogui.click(scr_w*0.5,scr_h*0.5)
        time.sleep(1)
        click("summon_skip.png")
        click("summon_skip.png")
        click("summon_comfirm.png",0.95)
    else:
        ans=False
    
    click("summon_equipment.png")
    if click("summon_free.png",0.95,2):
        time.sleep(2)
        pyautogui.click(scr_w*0.5,scr_h*0.5)
        time.sleep(1)
        click("summon_skip.png")
        click("summon_comfirm.png",0.95)
    else:
        ans=False
    
    goback()
    return ans


#福利(finish)
def welfare():
    ans=True
    click("welfare.png")
    click("welfare_banquet.png")
    if not click("welfare_banquet_free.png",0.9,2):
        ans=False
    goback()
    return ans

#特惠礼包(finish)
def gift():
    ans=True
    
    click("gift.png")
    pyautogui.moveTo(find("gift_cycle.png"))
    pyautogui.drag(0,-5000,duration=1)
    click("gift_diamond.png")
    if click("gift_claim.png",0.95,2):
        pyautogui.click(scr_w*0.5,scr_h*0.75)
        time.sleep(1)
    else:
        ans=False

    click("gift_resource.png")
    if click("gift_claim.png",0.95,2):
        pyautogui.click(scr_w*0.5,scr_h*0.75)
        time.sleep(1)
    else:
        ans=False

    goback()
    return ans

#失控练成阵(finish)
def pvp1():
    ans=True
    
    click("pvp.png")
    click("pvp1.png")
    if not click("pvp1_claim.png",0.8,4):
        ans=False
    goback()
    return ans

#竞技场(finish)
def pvp2():
    ans=True
    click("pvp.png")
    click("pvp2.png")
    for i in range(5):
        position=find("pvp2_ranking.png")
        time.sleep(1)
        for i in range(3):
            pyautogui.moveTo(position.x,position.y+scr_h/2)
            pyautogui.drag(0,-5000,duration=1)
        time.sleep(1)
        
        position=find("none_ranking.png")
        position_b=find("challenge.png")
        pyautogui.click(position_b.x,position.y)
        
        change("team6.png","team6_enable.png",0.9)
        #no more try->goback
        if not click("fight.png",0.8,2):
            ans=False
            break
        if find("pvp2_moreTry.png",0.8,2):
            ans=False
            break
        while not locate("pvp2_battleWin.png"):
            time.sleep(1)
        click("exit.png")
    goback()
    return ans

#竞技场领奖(finish)
def pvp2_reward():
    ans=True
    click("pvp.png")
    click("pvp2.png")
    ans=click("pvp2_reward.png",0.8,2)and ans
    ans=click("pvp2_claim.png",0.8,2)and ans
    goback()
    
    return ans

#荣耀之巅(finish)
def pvp4():
    click("pvp.png")
    click("pvp4.png")
    click("pvp4_challenge.png")
    if find("pvp4_moretry.png",0.8,2):
        goback()
        return False
    for i in range(5):
        click("next_team.png",0.8,2)
        click("next_team.png",0.8,2)
        click("start_pairing.png")

        while not locate("re_pairing.png"):
            pyautogui.click(scr_w*0.5,scr_h*0.9)
            time.sleep(1)
        click("re_pairing.png")
        
        if find("pvp4_moretry.png",0.8,2):
            pyautogui.press("esc")
            time.sleep(1)
            click("pvp4_exit.png")
            goback()
            return False
    goback()
    return True

def pvp4_reward():
    click("pvp.png")
    click("pvp4.png")
    position=find("pvp4_flag.png")
    time.sleep(1)
    pyautogui.click(position.x,scr_h-50)

    goback()

#公会(finish)
def guild():
    click("guild.png")
    if find("guild_signInText.png",0.8,2):
        pyautogui.press("esc")
    time.sleep(1)
    
    click("guild_mining.png")
    click("guild_miningclaim.png",0.9,2)
    while not find("guild_startmining.png"):
        pyautogui.click(scr_w/2,0)
        time.sleep(1)
    click("guild_startmining.png")
    pyautogui.press("esc")
    time.sleep(1)
    
    click("guild_signIn.png")
    
    
    click("guild_hall.png")
    position=find("guild_donate.png")
    for i in range(12):
        if(position==False):
            break
        pyautogui.click(position)
        time.sleep(2)
        
    click("guild_contributionReward.png")
    click("guild_100contributionReward.png",0.8,2)
    click("guild_100contributionReward_unenable.png",0.8,2)
    goback()

#社交(finish)
def friend():
    click("friend.png")
    click("friend_claim.png",0.95,2)
    goback()
    click("friend.png")
    click("friend_give.png",0.95,2)
    goback()

#冒险-讨伐(finish)
def campaign():
    click("adventure.png")
    click("campaign.png")
    time.sleep(1)
    pyautogui.click((scr_w*0.25,scr_h*0.5))
    time.sleep(1)
    position=find("campaign_firstPart.png")
    pyautogui.moveTo(position.x,position.y+scr_h*0.12)
    pyautogui.drag(0,5000,duration=1)
    time.sleep(1)
    click("campaign_6.png",0.8,2)
    pyautogui.click((scr_w*0.388,scr_h*0.95))
    time.sleep(1)
    position=find("campaign_text.png")
    pyautogui.moveTo(position.x,position.y+scr_h*0.5)
    pyautogui.drag(0,-5000,duration=1)
    time.sleep(1)
    position=find("campaign_rewardA.png",0.95,2)
    if(position==False):
        goback()
        return False
    pyautogui.click(position)
    time.sleep(1)
    pyautogui.click((scr_w*0.7,scr_h*0.8))
    
    goback()
    return True

#素材关卡(finish)
def material():
    click("adventure.png")
    click("material.png")
    time.sleep(4)
    pyautogui.click((scr_w*0.038,scr_h*0.69))
    time.sleep(2)
    pyautogui.click((scr_w*0.825,scr_h*0.64))
    time.sleep(2)
    for i in range(10):
        pyautogui.click((scr_w*0.5,scr_h*0.804))
        time.sleep(2)
    goback()
    return True

#辉煌航迹(finish?)
def sail():
    click("adventure.png")
    click("sail.png")
    click("sail_novicePart.png")
    click("sail_readyFight.png")
    if not click("sail_fightBegain.png",0.95,2):
        goback()
        return False
    while not locate("sail_trialCompleted.png"):
        time.sleep(2)
    goback()
    return True
def sail_reward():
    click("adventure.png")
    click("sail.png")
    click("sail_reward.png")
    click("sail_claim.png")

    goback()
    return True

def market():
    click("market.png")
    changeClick("market_permanent.png","market_permanent_unenable.png")
    changeClick("market_generalPart.png","market_generalPart.png_enable.png")
    click("market_5000.png",0.95)
    click("market_MAX.png",0.95)
    click("market_buy.png",0.95)
    click("market_comfirm.png",0.95)
    goback()

