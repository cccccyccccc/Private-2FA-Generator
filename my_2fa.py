import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyotp
import time
import json
import os
import pyperclip  #用于复制到剪贴板

# 数据保存的文件名
DATA_FILE = "secrets.json"

class AuthenticatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("我的专属 2FA 验证器")
        self.root.geometry("400x500")
        
        # 存储账号信息的列表 [{'name': 'Google', 'secret': 'KJ...'}]
        self.accounts = self.load_data()
        
        # 界面布局
        self.setup_ui()
        
        # 启动定时刷新循环
        self.update_codes()

    def setup_ui(self):
        # 顶部：添加按钮
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill="x")
        
        add_btn = tk.Button(top_frame, text="+ 添加新账号", command=self.add_account, bg="#007bff", fg="white", font=("Arial", 10, "bold"))
        add_btn.pack()

        # 中部：滚动区域显示验证码
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10)
        self.scrollbar.pack(side="right", fill="y")

        # 底部：倒计时进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=30)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        
        self.time_label = tk.Label(self.root, text="30s", font=("Arial", 8))
        self.time_label.pack(pady=(0, 5))

        # 用于存储界面上的Label引用，以便更新文字
        self.code_labels = []

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.accounts, f)

    def add_account(self):
        # 弹出对话框输入信息
        name = simpledialog.askstring("添加账号", "请输入账号名称 (例如: Google):")
        if not name: return
        
        secret = simpledialog.askstring("添加密钥", "请输入密钥 (Base32 Key):")
        if not secret: return
        
        # 去除空格并大写
        secret = secret.replace(" ", "").upper()
        
        # 验证密钥是否合法
        try:
            pyotp.TOTP(secret).now()
        except:
            messagebox.showerror("错误", "无效的密钥格式！通常是一串字母和数字的组合。")
            return

        self.accounts.append({"name": name, "secret": secret})
        self.save_data()
        self.refresh_ui_list()

    def copy_code(self, code):
        pyperclip.copy(code)
        messagebox.showinfo("复制成功", f"验证码 {code} 已复制到剪贴板！", parent=self.root)

    def refresh_ui_list(self):
        # 清空现有列表重建
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.code_labels = []

        for acc in self.accounts:
            frame = tk.Frame(self.scrollable_frame, pady=5, relief="groove", bd=1)
            frame.pack(fill="x", pady=2)

            # 账号名称
            lbl_name = tk.Label(frame, text=acc['name'], font=("Arial", 10, "bold"), anchor="w")
            lbl_name.pack(fill="x", padx=5)

            # 验证码 (使用大号字体)
            lbl_code = tk.Label(frame, text="------", font=("Courier", 24, "bold"), fg="#333")
            lbl_code.pack(padx=5)
            
            # 点击复制功能
            lbl_code.bind("<Button-1>", lambda e, c=lbl_code: self.copy_code(c.cget("text")))
            
            # 存储引用以便后续更新
            self.code_labels.append({"label": lbl_code, "secret": acc['secret']})

    def update_codes(self):
        # 获取当前时间戳
        now = time.time()
        # TOTP 周期通常是 30 秒
        period = 30
        time_remaining = period - (now % period)
        
        # 更新进度条
        self.progress_var.set(time_remaining)
        self.time_label.config(text=f"刷新剩余: {int(time_remaining)}秒")

        # 只要列表不为空，就重新计算验证码
        # 注意：为了性能，通常只有当 current_code 改变时才去更新UI文字，
        # 但这里为了代码简单，每秒刷新一次文字也无妨
        if not self.code_labels and self.accounts:
            self.refresh_ui_list()

        for item in self.code_labels:
            try:
                totp = pyotp.TOTP(item['secret'])
                current_code = totp.now()
                # 给验证码中间加个空格，方便阅读 (例如 123 456)
                display_code = f"{current_code[:3]} {current_code[3:]}"
                item['label'].config(text=display_code)
                
                # 如果剩余时间少于5秒，把字变红提醒
                if time_remaining < 5:
                    item['label'].config(fg="red")
                else:
                    item['label'].config(fg="#333")
            except:
                item['label'].config(text="Key Error")

        # 每 1000 毫秒 (1秒) 调用一次自己
        self.root.after(1000, self.update_codes)

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthenticatorApp(root)
    root.mainloop()