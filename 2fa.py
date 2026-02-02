import customtkinter as ctk
import pyotp
import time
import json
import os
import pyperclip
from tkinter import messagebox
from cryptography.fernet import Fernet


DATA_FILE = "secrets.json"
KEY_FILE = "master.key"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SecurityManager:
    def __init__(self):
        self.key = self.load_or_create_key()
        self.cipher = Fernet(self.key)

    def load_or_create_key(self):
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            return key

    def encrypt_data(self, data_list):
        json_str = json.dumps(data_list)
        return self.cipher.encrypt(json_str.encode('utf-8'))

    def decrypt_data(self, encrypted_bytes):
        try:
            return json.loads(self.cipher.decrypt(encrypted_bytes).decode('utf-8'))
        except:
            return []


class AuthCard(ctk.CTkFrame):
    def __init__(self, master, name, secret, copy_callback, edit_callback):
        super().__init__(master, fg_color="#2b2b2b", corner_radius=15)
        self.secret = secret
        self.copy_callback = copy_callback
        self.edit_callback = edit_callback
        self.configure(cursor="hand2")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.lbl_name = ctk.CTkLabel(
            self, text=name, font=("Microsoft YaHei UI", 14, "bold"),
            text_color="#a0a0a0", anchor="w", cursor="hand2"
        )
        self.lbl_name.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))
        self.lbl_code = ctk.CTkLabel(
            self, text="--- ---", font=("Consolas", 28, "bold"), text_color="#ffffff", cursor="hand2"
        )
        self.lbl_code.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        self.btn_copy = ctk.CTkButton(
            self, text="复制", width=60, height=30, fg_color="#3a3a3a",
            hover_color="#005fb8", corner_radius=8,
            command=lambda: self.copy_callback(self.lbl_code.cget("text"))
        )
        self.btn_copy.grid(row=0, column=1, rowspan=2, padx=15)

        self.bind("<Button-1>", self.on_click)
        self.lbl_name.bind("<Button-1>", self.on_click)
        self.lbl_code.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        self.edit_callback()

    def update_code(self, time_remaining):
        try:
            totp = pyotp.TOTP(self.secret)
            code = totp.now()
            self.lbl_code.configure(text=f"{code[:3]} {code[3:]}")
            self.lbl_code.configure(text_color="#ff5555" if time_remaining < 5 else "#ffffff")
        except:
            self.lbl_code.configure(text="ERROR", text_color="red")


# --- 主程序 ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.security = SecurityManager()

        self.title("安全验证器")
        self.geometry("420x600")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.accounts = self.load_data()
        self.cards = []
        self.current_edit_index = None

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        self.lbl_title = ctk.CTkLabel(self.header_frame, text="安全验证器", font=("Microsoft YaHei UI", 24, "bold"))
        self.lbl_title.pack(side="left")

        self.btn_nav = ctk.CTkButton(
            self.header_frame, text="+", width=40, height=40, corner_radius=20,
            font=("Arial", 20), fg_color="#0067c0", hover_color="#005a9e",
            command=self.show_add_page
        )
        self.btn_nav.pack(side="right")

        self.home_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.home_frame.grid_rowconfigure(1, weight=1)
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.entry_search = ctk.CTkEntry(
            self.home_frame, placeholder_text="搜索账号...", height=35,
            corner_radius=18, border_width=0, fg_color="#2b2b2b", text_color="#ffffff"
        )
        self.entry_search.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 15))

        self.scroll_frame = ctk.CTkScrollableFrame(self.home_frame, corner_radius=0, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(self.home_frame, height=4, progress_color="#0067c0")
        self.progress.grid(row=2, column=0, sticky="ew", padx=0, pady=(10, 0))
        self.progress.set(1.0)

        self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_frame.grid_columnconfigure(0, weight=1)
        self.setup_add_frame()

        self.edit_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.edit_frame.grid_columnconfigure(0, weight=1)
        self.setup_edit_frame()
        self.refresh_list()
        self.show_home_page()
        self.update_clock()

    def setup_add_frame(self):
        ctk.CTkLabel(self.add_frame, text="添加新账号", font=("Microsoft YaHei UI", 20, "bold"),
                     text_color="#ffffff").pack(pady=(30, 20))

        ctk.CTkLabel(self.add_frame, text="账号名称 (Name)", font=("Microsoft YaHei UI", 14), text_color="#a0a0a0",
                     anchor="w").pack(fill="x", padx=30, pady=(10, 5))
        self.entry_add_name = ctk.CTkEntry(self.add_frame, height=40, corner_radius=8, border_width=0,
                                           fg_color="#2b2b2b")
        self.entry_add_name.pack(fill="x", padx=30, pady=(0, 15))

        ctk.CTkLabel(self.add_frame, text="密钥 (Secret Key)", font=("Microsoft YaHei UI", 14), text_color="#a0a0a0",
                     anchor="w").pack(fill="x", padx=30, pady=(10, 5))
        self.entry_add_secret = ctk.CTkEntry(self.add_frame, height=40, corner_radius=8, border_width=0,
                                             fg_color="#2b2b2b")
        self.entry_add_secret.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkButton(self.add_frame, text="确认添加", height=45, corner_radius=10, fg_color="#0067c0",
                      hover_color="#005a9e", font=("Microsoft YaHei UI", 14, "bold"),
                      command=self.save_new_account).pack(fill="x", padx=30, pady=20)

    def setup_edit_frame(self):
        ctk.CTkLabel(self.edit_frame, text="编辑账号", font=("Microsoft YaHei UI", 20, "bold"),
                     text_color="#ffffff").pack(pady=(30, 20))
        ctk.CTkLabel(self.edit_frame, text="修改名称", font=("Microsoft YaHei UI", 14), text_color="#a0a0a0",
                     anchor="w").pack(fill="x", padx=30, pady=(10, 5))
        self.entry_edit_name = ctk.CTkEntry(self.edit_frame, height=40, corner_radius=8, border_width=0,
                                            fg_color="#2b2b2b")
        self.entry_edit_name.pack(fill="x", padx=30, pady=(0, 15))

        ctk.CTkButton(self.edit_frame, text="保存修改", height=45, corner_radius=10, fg_color="#0067c0",
                      hover_color="#005a9e", font=("Microsoft YaHei UI", 14, "bold"),
                      command=self.save_edit_account).pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkButton(self.edit_frame, text="删除账号", height=45, corner_radius=10, fg_color="#d32f2f",
                      hover_color="#b71c1c", font=("Microsoft YaHei UI", 14, "bold"), command=self.delete_account).pack(
            fill="x", padx=30, pady=10)

    def show_home_page(self):
        self.add_frame.grid_forget()
        self.edit_frame.grid_forget()
        self.home_frame.grid(row=1, column=0, sticky="nsew")

        self.lbl_title.configure(text="安全验证器")
        self.btn_nav.configure(text="+", command=self.show_add_page)
        self.entry_add_name.delete(0, 'end')
        self.entry_add_secret.delete(0, 'end')

    def show_add_page(self):
        self.home_frame.grid_forget()
        self.edit_frame.grid_forget()
        self.add_frame.grid(row=1, column=0, sticky="nsew")

        self.lbl_title.configure(text=" ")
        self.btn_nav.configure(text="<", command=self.show_home_page)
        self.entry_add_name.focus()

    def show_edit_page(self, index):
        """进入编辑模式，填充数据"""
        self.current_edit_index = index
        data = self.accounts[index]

        self.home_frame.grid_forget()
        self.add_frame.grid_forget()
        self.edit_frame.grid(row=1, column=0, sticky="nsew")

        self.lbl_title.configure(text=" ")
        self.btn_nav.configure(text="<", command=self.show_home_page)
        self.entry_edit_name.delete(0, 'end')
        self.entry_edit_name.insert(0, data['name'])

    def save_new_account(self):
        name = self.entry_add_name.get()
        secret = self.entry_add_secret.get().replace(" ", "").upper()
        if not name or not secret: return

        try:
            pyotp.TOTP(secret).now()
            self.accounts.append({"name": name, "secret": secret})
            self.save_data()
            self.refresh_list()
            messagebox.showinfo("成功", "账号添加成功！")
            self.show_home_page()
        except:
            messagebox.showerror("错误", "密钥格式无效")

    def save_edit_account(self):
        """保存修改"""
        if self.current_edit_index is None: return
        new_name = self.entry_edit_name.get()
        if not new_name: return
        self.accounts[self.current_edit_index]['name'] = new_name
        self.save_data()
        self.refresh_list()
        self.show_home_page()

    def delete_account(self):
        """删除账号"""
        if self.current_edit_index is None: return

        confirm = messagebox.askyesno("确认删除", "确定要删除这个账号吗？\n此操作无法撤销。")
        if confirm:
            del self.accounts[self.current_edit_index]
            self.save_data()
            self.refresh_list()
            self.show_home_page()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "rb") as f:
                    data = f.read()
                    if not data: return []
                    return self.security.decrypt_data(data)
            except:
                return []
        return []

    def save_data(self):
        try:
            encrypted = self.security.encrypt_data(self.accounts)
            with open(DATA_FILE, "wb") as f:
                f.write(encrypted)
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def copy_to_clipboard(self, code):
        pyperclip.copy(code.replace(" ", ""))

    def refresh_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.cards = []
        for i, acc in enumerate(self.accounts):
            card = AuthCard(
                self.scroll_frame,
                acc['name'],
                acc['secret'],
                copy_callback=self.copy_to_clipboard,
                edit_callback=lambda index=i: self.show_edit_page(index)
            )
            card.pack(fill="x", pady=5, padx=5)
            self.cards.append(card)

    def update_clock(self):
        now = time.time()
        period = 30
        remaining = period - (now % period)
        self.progress.set(remaining / period)
        if self.home_frame.winfo_viewable():
            for card in self.cards:
                card.update_code(remaining)
        self.after(1000, self.update_clock)


if __name__ == "__main__":
    app = App()
    app.mainloop()