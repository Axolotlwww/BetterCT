from pynput import keyboard
from pynput.mouse import Controller as MouseController

# 创建鼠标控制器实例，用于获取坐标
mouse = MouseController()

def on_press(key):
    """键盘按下回调函数"""
    if key == keyboard.Key.space:
        # 获取当前鼠标坐标（x, y）
        x, y = mouse.position
        print(f"鼠标坐标: ({x}, {y})")
    elif key == keyboard.Key.esc:
        # 按 ESC 退出监听
        return False

# 启动键盘监听（非阻塞式，但使用 join 保持运行）        
print("程序已启动。按下 空格键 打印鼠标坐标，按下 ESC 退出。")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()