import tkinter as tk
from PIL import Image, ImageTk
import pygame  # 需要安装：pip install pygame

# 初始化 pygame 音频
pygame.mixer.init()

# 创建主窗口
root = tk.Tk()
root.title("悬停旋转+循环音频")
root.geometry("400x400")

# 加载图片（请替换为你的图片路径）
image_path = "1.png"
original_image = Image.open(image_path)
original_image = original_image.resize((200, 200))  # 可根据需要调整大小

# 初始 PhotoImage 对象
tk_image = ImageTk.PhotoImage(original_image)

# 显示图片的 Label
label = tk.Label(root, image=tk_image, bd=0)
label.pack(pady=50)

# 动画状态变量
is_hovering = False
angle = 0

# 音频文件路径（支持 mp3, wav 等 pygame 可播放格式）
audio_path = "your_audio.mp3"

def play_audio():
    """加载并循环播放音频"""
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play(loops=-1)  # -1 表示无限循环

def stop_audio():
    """停止音频播放"""
    pygame.mixer.music.stop()

def rotate_image():
    """执行旋转动画"""
    global angle
    if is_hovering:
        angle = (angle + 10) % 360  # 每次旋转10度
        rotated_img = original_image.rotate(angle)
        global tk_image
        tk_image = ImageTk.PhotoImage(rotated_img)
        label.config(image=tk_image)
        # 50ms 后再次执行，形成连续旋转
        root.after(50, rotate_image)

def on_enter(event):
    """鼠标进入控件"""
    global is_hovering
    if not is_hovering:
        is_hovering = True
        rotate_image()      # 开始旋转
        play_audio()        # 开始播放音频

def on_leave(event):
    """鼠标离开控件"""
    global is_hovering
    if is_hovering:
        is_hovering = False
        stop_audio()        # 停止音频
        # 可选：恢复原始图像
        global tk_image
        tk_image = ImageTk.PhotoImage(original_image)
        label.config(image=tk_image)
        angle = 0           # 重置角度

# 绑定事件到 Label（也可以是 Button）
label.bind("<Enter>", on_enter)
label.bind("<Leave>", on_leave)

root.mainloop()