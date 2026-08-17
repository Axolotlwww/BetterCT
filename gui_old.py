import tkinter as tk

root = tk.Tk()
root.title("BetterCT")
root.geometry("900x600")
root.configure(bg="#000")

#框架
titleBar=tk.Frame(root)
titleBar.pack(side="top",fill="x")

titleBar_content=tk.Frame(titleBar)
titleBar_content.pack(fill="both",padx=20,pady=10)

sideBar=tk.Frame(root)
sideBar.pack(side="left",fill="y")

sideBar_content=tk.Frame(sideBar,width=100)
sideBar_content.pack(side="left",fill="both",padx=10,pady=10)
sideBar_content.pack_propagate(False)

contentPage=tk.Frame(root,bg="#444")
contentPage.pack(side="right",fill="both")

def set_bg(frame,color):
    try:
        frame.configure(bg=color)
    except:
        print(f"{frame}无法被bg")
        pass
    for child in frame.winfo_children():
        set_bg(child,color)

 def home:
     

title=tk.Label(titleBar_content,text="BetterCT",font=("等线",24),fg="#ccc")
title.pack(side="left")

home=tk.Button(sideBar_content,text="主页",font=("等线",20),fg="#ccc",bd=0,pady=5,command=home)
home.pack(side="top")
home=tk.Button(sideBar_content,text="设置",font=("等线",20),fg="#ccc",bd=0,pady=5)
home.pack(side="top")


set_bg(titleBar,"#222")
set_bg(sideBar,"#333")
set_bg(contentPage,"#444")

root.mainloop()