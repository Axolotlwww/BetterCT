import tkinter as tk
from tkinter import ttk
import threading
import multiprocessing
import queue
import time
import webbrowser
import json
import main
import os
import sys

# ==================== 任务函数（模拟外部库，会阻塞） ====================
# 这些函数会被替换为另一个库内的函数，请确保它们可以被 pickle（顶层函数）


# ==================== 任务列表（顺序即显示顺序，可拖拽调整） ====================
tasks = [
    {"name": "启动游戏(务必放在最前面)", "func": main.openGame, "active": True,  "last_result": None},
    {"name": "邮件", "func": main.email, "active": True,  "last_result": None},
    {"name": "免费召唤", "func": main.summon, "active": True, "last_result": None},
    {"name": "福利", "func": main.welfare, "active": True, "last_result": None},
    {"name": "特惠礼包", "func": main.gift, "active": True, "last_result": None},
    {"name": "失控练成阵", "func": main.pvp1, "active": True, "last_result": None},
    {"name": "竞技场", "func": main.pvp2, "active": True, "last_result": None},
    {"name": "竞技场领奖", "func": main.pvp2_reward, "active": True, "last_result": None},
    {"name": "荣耀之巅", "func": main.pvp4, "active": True, "last_result": None},
    {"name": "荣耀之巅领奖", "func": main.pvp4_reward, "active": True, "last_result": None},
    {"name": "公会", "func": main.guild, "active": True, "last_result": None},
    {"name": "社交", "func": main.friend, "active": True, "last_result": None},
    {"name": "冒险-讨伐", "func": main.campaign, "active": True, "last_result": None},
    {"name": "冒险-素材关卡", "func": main.material, "active": True, "last_result": None},
    {"name": "冒险-辉煌航迹", "func": main.sail, "active": True, "last_result": None},
    {"name": "冒险-辉煌航迹领奖", "func": main.sail_reward, "active": True, "last_result": None},
    {"name": "集市", "func": main.market, "active": True, "last_result": None},
]

CONFIG_FILE = "task_config.json"

# ==================== 全局状态 ====================
busy = False                      # 是否正在运行任务
current_process = None            # 当前子进程对象
stop_event = threading.Event()    # 用于通知后台线程强制结束
busy_lock = threading.Lock()      # 保护 busy 标志
ui_queue = queue.Queue()          # 后台线程 -> 主线程 消息队列
task_rows = []                    # 与 tasks 顺序对应的行 Frame 列表（任务设置页）
drag_index = None                 # 拖拽排序时的源索引

cancel_all = threading.Event()   # 用于中止一键启动的整个顺序

def get_base_path():
    """返回可执行文件所在目录（打包后为 exe 所在文件夹，开发时为项目根目录）"""
    if getattr(sys, 'frozen', False):
        # 打包后，sys.executable 是 exe 的完整路径
        return os.path.dirname(sys.executable)
    else:
        # 开发环境，返回当前工作目录（你的项目文件夹）
        return os.path.abspath(".")
    
def load_config():
    """从 JSON 文件加载任务顺序和激活状态，并更新全局 tasks 列表。"""
    global tasks
    config_file = os.path.join(get_base_path(), CONFIG_FILE)   # 新增这一行
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        # config 预期格式：[{"name": "任务一", "active": true}, ...]
        # 根据名字重新排序 tasks，并更新 active
        new_tasks = []
        for item in config:
            for task in tasks:
                if task["name"] == item["name"]:
                    task["active"] = item.get("active", task["active"])
                    new_tasks.append(task)
                    break
        # 补充未在配置中出现的任务（例如新增任务），保持原顺序
        for task in tasks:
            if task not in new_tasks:
                new_tasks.append(task)
        tasks = new_tasks
    except FileNotFoundError:
        # 首次运行，使用默认配置
        pass
    except (json.JSONDecodeError, KeyError, TypeError):
        # 配置文件损坏，忽略并使用默认配置
        pass

def save_config():
    """将当前任务顺序和激活状态保存到 JSON 文件。"""
    config = [{"name": task["name"], "active": task["active"]} for task in tasks]
    config_file = os.path.join(get_base_path(), CONFIG_FILE)
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except IOError:
        # 忽略保存错误（例如权限问题）
        pass

# ==================== 子进程工作函数 ====================
def task_worker(func, result_queue):
    """在子进程中执行任务函数，并将结果放入队列。"""
    try:
        result = func()
        result_queue.put(result)
    except Exception:
        result_queue.put(False)


# ==================== 执行任务（后台线程中运行） ====================
def try_acquire_busy():
    global busy
    with busy_lock:
        if busy:
            return False
        busy = True
        return True


def release_busy():
    global busy
    with busy_lock:
        busy = False


def execute_task(task):
    """执行单个任务。必须在后台线程中调用，避免阻塞 GUI。"""
    global current_process
    if not try_acquire_busy():
        return

    stop_event.clear()
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=task_worker, args=(task["func"], q))
    current_process = p
    p.start()

    result = False
    interrupted = False

    try:
        while True:
            # 如果按下 F12，stop_event 会被设置
            if stop_event.is_set():
                if p.is_alive():
                    p.terminate()
                interrupted = True
                break

            try:
                result = q.get(timeout=0.1)
                break
            except queue.Empty:
                if not p.is_alive():
                    # 子进程异常退出
                    result = False
                    break
                continue
            except EOFError:
                # 子进程被强制终止
                interrupted = True
                break
    finally:
        p.join()
        current_process = None
        release_busy()

    # 将结果发送给主线程更新 UI
    final_result = "interrupted" if interrupted else result
    ui_queue.put((task, final_result))


def run_all_activated():
    """按当前 tasks 顺序依次执行所有已激活任务。"""
    for task in tasks:
        if cancel_all.is_set():            # 用户按下 F12，立即停止
            break
        if task["active"]:
            execute_task(task)


# ==================== 按钮回调 ====================
def on_trigger_task(task):
    """单个任务触发按钮回调。"""
    if busy:
        return
    threading.Thread(target=execute_task, args=(task,), daemon=True).start()


def on_start_all():
    """主页启动按钮回调。"""
    if busy:
        return
    cancel_all.clear()
    threading.Thread(target=run_all_activated, daemon=True).start()


def on_f12(event):
    """按下 F12 强制结束当前子进程。"""
    global current_process
    cancel_all.set()
    if busy and current_process and current_process.is_alive():
        stop_event.set()
        current_process.terminate()


# ==================== UI 更新 ====================
def apply_task_row_color(task, row):
    """根据任务最近一次结果设置行背景色。"""
    result = task.get("last_result")
    if result is True:
        color = "#c8e6c9"       # 浅绿
    elif result is False:
        color = "#ffcdd2"       # 浅红
    elif result == "interrupted":
        color = "#ffe0b2"       # 橙色
    else:
        color = "SystemButtonFace"
    row.configure(bg=color)
    for child in row.winfo_children():
        child.configure(bg=color)


def refresh_all_row_colors():
    """刷新所有任务行背景色（拖拽排序后调用）。"""
    for i, row in enumerate(task_rows):
        apply_task_row_color(tasks[i], row)


def update_task_row_color(task, result):
    """主线程中更新任务行颜色，并保存结果。"""
    task["last_result"] = result
    try:
        idx = tasks.index(task)
        if idx < len(task_rows):
            row = task_rows[idx]
            if row.winfo_exists():
                apply_task_row_color(task, row)
    except ValueError:
        pass


def poll_ui_queue(root):
    if not root.winfo_exists():   # 窗口已销毁，停止轮询
        return
    try:
        while True:
            task, result = ui_queue.get_nowait()
            update_task_row_color(task, result)
    except queue.Empty:
        pass
    root.after(100, poll_ui_queue, root)


# ==================== 页面构建 ====================
def show_page(page_name, content_frame):
    """切换右侧内容页。"""
    for widget in content_frame.winfo_children():
        widget.destroy()

    if page_name == "home":
        build_home_page(content_frame)
    elif page_name == "tasks":
        build_task_settings_page(content_frame)
    elif page_name == "about":
        build_about_page(content_frame)


def build_home_page(parent):
    """主页页面。"""
    info = tk.Label(
        parent,
        text="尊敬的机长,欢迎使用BetterCT😋😋😋\n\n请先阅读\"关于\"谢谢喵\n点击启动会按照顺序执行任务,也可以单独运行任务\n脚本未完工,详情请跳转github阅读",
        justify="left",
        font=("等线", 14),
    )
    info.pack(pady=20, padx=20, anchor="w")

    start_btn = tk.Button(
        parent,
        text="启动",
        command=on_start_all,
        width=15,
        height=2,
        bg="#4CAF50",
        fg="#ddd",
        font=("等线", 16),
        relief="flat"
    )
    start_btn.pack(side="bottom", anchor="se", padx=20, pady=20)


def build_task_settings_page(parent):
    """任务设置页面：竖向延申的任务列表。"""
    global task_rows
    task_rows = []

    # 列表容器
    list_frame = tk.Frame(parent)
    list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    for task in tasks:
        make_task_row(list_frame, task)


def make_task_row(parent, task):
    """创建单个任务行。"""
    row = tk.Frame(parent, relief="ridge", borderwidth=1, padx=5, pady=5)
    row.pack(side="top", fill="x", padx=5, pady=2)

    # 左侧拖动把手
    drag_label = tk.Label(row, text="≡", font=("Arial", 14), cursor="fleur")
    drag_label.pack(side="left", padx=5)
    drag_label.bind("<Button-1>", lambda e, t=task: start_drag(e, t))
    drag_label.bind("<B1-Motion>", lambda e: drag_motion(e))
    drag_label.bind("<ButtonRelease-1>", lambda e: end_drag(e))

    # 功能文字
    name_label = tk.Label(row, text=task["name"], width=20, anchor="w", font=("Arial", 11))
    name_label.pack(side="left", padx=5)

    # 右侧激活开关
    active_var = tk.BooleanVar(value=task["active"])

    def on_active_change(*args, t=task, var=active_var):
        t["active"] = var.get()
        save_config() 

    active_var.trace_add("write", on_active_change)
    check = tk.Checkbutton(row, text="激活", variable=active_var)
    check.pack(side="right", padx=5)

    # 右侧单独触发按钮
    trigger_btn = tk.Button(
        row,
        text="触发",
        command=lambda t=task: on_trigger_task(t),
        width=8,
    )
    trigger_btn.pack(side="right", padx=5)

    # 保存行引用
    task_rows.append(row)

    # 设置初始背景色
    apply_task_row_color(task, row)


def build_about_page(parent):
    """关于页面。"""
    title = tk.Label(parent, text="关于", font=("等线", 16, "bold"))
    title.pack(pady=10)

    version = tk.Label(parent, text="版本号：1.0.0", font=("等线", 11))
    version.pack(pady=5)

    disclaimer = tk.Label(
        parent,
        text="免责声明：本软件仅供学习交流使用\n作者不为程序作任何保证(包括功能能否正常运行)\n最好在1920x1080 60帧的环境下使用(因为其他没测过)\n大狗粪代码没有考虑任何优化💩",
        justify="left",
        wraplength=400,
        font=("等线", 14),
    )
    disclaimer.pack(pady=5, padx=20)

    link = tk.Label(
        parent,
        text="GitHub: https://github.com/Axolotlwww/BetterCT",
        fg="blue",
        cursor="hand2",
        font=("Arial", 10),
    )
    link.pack(pady=5)
    link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/your-repo"))


# ==================== 拖拽排序 ====================
def start_drag(event, task):
    global drag_index
    try:
        drag_index = tasks.index(task)
    except ValueError:
        drag_index = None


def drag_motion(event):
    global drag_index
    if drag_index is None:
        return

    # 找到鼠标下方的行
    target = None
    for i, row in enumerate(task_rows):
        y = row.winfo_rooty()
        h = row.winfo_height()
        if y <= event.y_root < y + h:
            target = i
            break

    if target is not None and target != drag_index:
        # 交换 tasks 和 task_rows
        tasks[drag_index], tasks[target] = tasks[target], tasks[drag_index]
        task_rows[drag_index], task_rows[target] = task_rows[target], task_rows[drag_index]

        # 重新按新顺序 pack 行
        for row in task_rows:
            row.pack_forget()
        for row in task_rows:
            row.pack(side="top", fill="x", padx=5, pady=2)

        # 刷新背景颜色，避免错乱
        refresh_all_row_colors()

        drag_index = target


def end_drag(event):
    global drag_index
    drag_index = None
    save_config() 

#加了个递归改背景颜色
def set_bg(widget, color):
    """递归设置 widget 及其所有子控件的背景色"""
    try:
        widget.configure(bg=color)
    except:
        pass  # 某些控件可能不支持 bg

    for child in widget.winfo_children():
        set_bg(child, color)
# ==================== 主程序 ====================
def main():
    load_config()
    root = tk.Tk()
    root.title("BetterCT")
    root.geometry("800x610")

    # 绑定 F12 强制终止
    root.bind_all("<F12>", on_f12)

    # ---------- 顶部标题栏 ----------
    header = tk.Frame(root, bg="#333", height=60)
    header.pack(side="top", fill="x")
    header.pack_propagate(False)

    logo = tk.Label(header, text="😋", font=("Arial", 24), bg="#333", fg="#ddd")
    logo.pack(side="left", padx=10, pady=10)

    title = tk.Label(header, text="BetterCT", font=("Arial", 20), bg="#333", fg="#ddd")
    title.pack(side="left", padx=5, pady=10)

    # ---------- 主体区域 ----------
    body = tk.Frame(root)
    body.pack(side="top", fill="both", expand=True)

    # 左侧侧边栏
    sidebar = tk.Frame(body, width=150, bg="#444")
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    btn_home = tk.Button(sidebar, text="主页", command=lambda: show_page("home", content_frame),fg="#ddd",relief="flat",font=("等线", 16))
    btn_home.pack(fill="x", padx=5, pady=5)

    btn_tasks = tk.Button(sidebar, text="任务", command=lambda: show_page("tasks", content_frame),fg="#ddd",relief="flat",font=("等线", 16))
    btn_tasks.pack(fill="x", padx=5, pady=5)

    btn_about = tk.Button(sidebar, text="关于", command=lambda: show_page("about", content_frame),fg="#ddd",relief="flat",font=("等线", 16))
    btn_about.pack(fill="x", padx=5, pady=5)

    # 右侧内容页
    content_frame = tk.Frame(body, bg="white")
    content_frame.pack(side="left", fill="both", expand=True)

    # 默认显示主页
    show_page("home", content_frame)

    # 启动 UI 消息轮询
    poll_ui_queue(root)
    
    set_bg(header,"#333")
    set_bg(sidebar,"#444")
    
    root.mainloop()


if __name__ == "__main__":
    # multiprocessing 在 Windows 上需要保护入口
    main()