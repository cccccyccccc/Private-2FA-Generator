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
        encrypted_bytes = self.cipher.encrypt(json_str.encode('utf-8'))
        return encrypted_bytes

    def decrypt_data(self, encrypted_bytes):
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            json_str = decrypted_bytes.decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            print(f"解密失败: {e}")
            return []


class AuthCard(ctk.CTkFrame):
    """自定义控件：单个账号的显示卡片"""

    def __init__(self, master, name, secret, copy_callback):
        super().__init__(master, fg_color="#2b2b2b", corner_radius=15)
        self.secret = secret
        self.copy_callback = copy_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.lbl_name = ctk.CTkLabel(
            self,
            text=name,
            font=("Microsoft YaHei UI", 14, "bold"),
            text_color="#a0a0a0",
            anchor="w"
        )
        self.lbl_name.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))

        self.lbl_code = ctk.CTkLabel(
            self,
            text="--- ---",
            font=("Consolas", 28, "bold"),
            text_color="#ffffff"
        )
        self.lbl_code.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        self.btn_copy = ctk.CTkButton(
            self,
            text="复制",
            width=60,
            height=30,
            fg_color="#3a3a3a",
            hover_color="#005fb8",
            corner_radius=8,
            command=lambda: self.copy_callback(self.lbl_code.cget("text"))
        )
        self.btn_copy.grid(row=0, column=1, rowspan=2, padx=15)

    def update_code(self, time_remaining):
        try:
            totp = pyotp.TOTP(self.secret)
            code = totp.now()
            display_code = f"{code[:3]} {code[3:]}"
            self.lbl_code.configure(text=display_code)

            if time_remaining < 5:
                self.lbl_code.configure(text_color="#ff5555")
            else:
                self.lbl_code.configure(text_color="#ffffff")
        except:
            self.lbl_code.configure(text="ERROR", text_color="red")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.security = SecurityManager()
        self.title("Private Authenticator")
        self.geometry("420x600")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.accounts = self.load_data()
        self.cards = []
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="安全验证器", font=("Microsoft YaHei UI", 24, "bold"))
        self.lbl_title.pack(side="left")
        self.btn_add = ctk.CTkButton(self.header_frame, text="+", width=40, height=40, corner_radius=20,
                                     font=("Arial", 20), fg_color="#0067c0", hover_color="#005a9e",
                                     command=self.add_account_dialog)
        self.btn_add.pack(side="right")
        self.entry_search = ctk.CTkEntry(self, placeholder_text="搜索账号...", height=35, corner_radius=18,
                                         border_width=0, fg_color="#2b2b2b", text_color="#ffffff")
        self.entry_search.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        self.scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.progress = ctk.CTkProgressBar(self, height=4, progress_color="#0067c0")
        self.progress.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        self.progress.set(1.0)
        self.refresh_list()
        self.update_clock()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "rb") as f:  # 注意是 'rb' 二进制读取
                    encrypted_data = f.read()
                    # 如果文件是空的
                    if not encrypted_data: return []
                    return self.security.decrypt_data(encrypted_data)
            except Exception as e:
                print(f"Error loading data: {e}")
                return []
        return []

    def save_data(self):
        try:
            encrypted_data = self.security.encrypt_data(self.accounts)
            with open(DATA_FILE, "wb") as f:  # 注意是 'wb' 二进制写入
                f.write(encrypted_data)
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def add_account_dialog(self):
        dialog = ctk.CTkInputDialog(text="输入账号名称 (如: Google):", title="添加账号")
        name = dialog.get_input()
        if not name: return

        dialog_secret = ctk.CTkInputDialog(text="输入密钥 (Base32):", title="添加密钥")
        secret = dialog_secret.get_input()
        if not secret: return

        secret = secret.replace(" ", "").upper()

        try:
            pyotp.TOTP(secret).now()
            self.accounts.append({"name": name, "secret": secret})
            self.save_data()
            self.refresh_list()
        except:
            messagebox.showerror("错误", "密钥格式无效")

    def copy_to_clipboard(self, code):
        clean_code = code.replace(" ", "")
        pyperclip.copy(clean_code)

    def refresh_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.cards = []
        for acc in self.accounts:
            card = AuthCard(self.scroll_frame, acc['name'], acc['secret'], self.copy_to_clipboard)
            card.pack(fill="x", pady=5, padx=5)
            self.cards.append(card)

    def update_clock(self):
        now = time.time()
        period = 30
        remaining = period - (now % period)
        self.progress.set(remaining / period)
        for card in self.cards:
            card.update_code(remaining)
        self.after(1000, self.update_clock)


if __name__ == "__main__":
    app = App()
    app.mainloop()