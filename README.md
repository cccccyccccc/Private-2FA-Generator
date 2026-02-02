
# 🔐 Win11 Style 2FA Authenticator

一个基于 Python 和 CustomTkinter 构建的桌面端两步验证（2FA）工具。拥有现代化的 Windows 11 深色磨砂风格界面，支持标准的 TOTP 算法（兼容 Google Authenticator）。

## ✨ 功能特点

- **🎨 现代 UI**：采用 Windows 11 风格设计，深色模式，圆角卡片布局。
- **🔒 本地安全**：所有密钥仅保存在本地 `secrets.json` 文件中，不上传云端，隐私完全可控。
- **⚡️ 实时刷新**：30秒自动刷新验证码，配备平滑倒计时进度条。
- **📋 一键复制**：点击复制按钮即可将验证码复制到剪贴板。
- **➕ 简易添加**：支持手动输入 Base32 密钥添加账户。

## 🛠️ 技术栈

- **Python 3.x**
- **CustomTkinter**: 用于构建现代化的 GUI 界面。
- **PyOTP**: 处理标准 TOTP (Time-Based One-Time Password) 算法。
- **Pyperclip**: 实现剪贴板操作。

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone [https://github.com/你的用户名/你的仓库名.git](https://github.com/你的用户名/你的仓库名.git)
cd 你的仓库名

```

### 2. 安装依赖

建议使用 Python 虚拟环境。

```bash
pip install customtkinter pyotp pyperclip packaging

```

### 3. 运行软件

```bash
python win11_2fa.py

```

## 📝 数据存储说明

当你添加账号后，程序会在根目录生成一个 `secrets.json` 文件。

* **请务必保管好此文件。**
* 如果你要迁移数据，只需复制此文件到新电脑的程序目录下即可。
* **注意**：此文件包含你的明文密钥，请勿发送给他人。

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来改进这个小工具！

## 📄 许可证

MIT License