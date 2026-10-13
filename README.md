# Cursor CLTO

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Stars](https://img.shields.io/github/stars/clto/cursor-clto)

**Cursor CLTO** - A powerful Python tool for Cursor account management and automation

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Introduction

Cursor CLTO is a comprehensive Python-based solution for managing Cursor accounts, featuring automated registration, machine ID reset, temporary email integration, and multi-language support.

### ✨ Key Highlights

- 🚀 **One-click Registration** - Automated Cursor account creation
- 🔄 **Machine ID Reset** - Bypass device limitations  
- 📧 **Temporary Email** - Integrated email service
- 🌍 **Multi-language** - Support for 12+ languages
- 🎨 **Beautiful UI** - Colorful terminal interface with emoji support

## 🎯 Features

### Core Functions

| Function | Description | Status |
|----------|-------------|--------|
| Reset Machine ID | Generate new device identifiers | ✅ Working |
| Register with Google | One-click Google OAuth registration | ✅ Working |
| Register with GitHub | One-click GitHub OAuth registration | ✅ Working |
| Custom Email Registration | Register with any email address | ✅ Working |
| Temporary Email | Auto-generate disposable emails | ✅ Working |
| Disable Auto-Update | Prevent automatic updates | ✅ Working |
| Full Reset | Complete Cursor data cleanup | ✅ Working |
| Version Bypass | Skip version verification | ✅ Working |
| Token Limit Bypass | Remove usage restrictions | ✅ Working |

### Supported Languages

🇺🇸 English • 🇨🇳 简体中文 • 🇹🇼 繁體中文 • 🇻🇳 Tiếng Việt • 🇳🇱 Nederlands • 🇩🇪 Deutsch • 🇫🇷 Français • 🇵🇹 Português • 🇷🇺 Русский • 🇹🇷 Türkçe • 🇧🇬 Български • 🇪🇸 Español

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows OS (other platforms coming soon)

### Installation

```bash
# Clone the repository
git clone https://github.com/clto/cursor-clto.git
cd cursor-clto

# Install dependencies
pip install colorama requests selenium

# Run the application
python main.py
```

### First Time Usage

1. Run `python main.py`
2. Select your language (press `8`)
3. Choose desired function from menu
4. Follow on-screen instructions

## 📋 Menu Options

```
0. Exit Program
1. Reset Machine ID
2. Register New Cursor Account
3. Register with Google Account ⭐
4. Register with GitHub Account ⭐
5. Register with Custom Email
6. Temporary GitHub Register
7. Close Cursor Application
8. Change Language
9. Disable Auto-Update
10. Totally Reset Cursor
11. Contribute to Project
12. Show Config
13. Select Chrome Profile
14. Delete Cursor Google Account
15. Bypass Version Check
16. Check User Authorized
17. Bypass Token Limit
```

## 🔧 Configuration

Edit `.env` file to customize settings:

```env
VERSION=1.0.0
LANGUAGE=en
CHROME_PROFILE=default
```

## 📁 Project Structure

```
cursor-clto/
├── main.py                 # Entry point
├── config.py              # Configuration manager
├── logo.py                # UI branding
├── utils.py               # Utility functions
├── cursor_register.py     # Registration logic
├── new_tempemail.py       # Email service
├── reset_machine_manual.py # Machine ID reset
├── new_signup.py          # Browser automation
├── locales/               # Translation files
│   ├── en.json
│   ├── zh_cn.json
│   └── ...
└── README.md
```

## 🛠️ Development

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py
```

### Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed main.py
```

## ❓ FAQ

### Q: How to change language?

A: Press `8` in main menu, then select your preferred language.

### Q: Registration fails?

A: Ensure you have stable internet connection and Chrome browser installed.

### Q: Where are config files stored?

A: Configuration is stored in `.env` file in project root.

### Q: Can I use this on Linux/Mac?

A: Currently optimized for Windows. Linux/Mac support coming soon.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original project by [Pin Studios (hovanhoa)](https://github.com/hovanhoa/cursor-free-vip)
- Contributors and community members
- All open-source libraries used

## 📞 Contact

- **Author**: clto
- **GitHub**: [@clto](https://github.com/clto)
- **Project Link**: [https://github.com/clto/cursor-clto](https://github.com/clto/cursor-clto)

## ⭐ Star History

If you find this project useful, please consider giving it a star! 

[![Star History Chart](https://api.star-history.com/svg?repos=clto/cursor-clto&type=Date)](https://star-history.com/#clto/cursor-clto&Date)

---

<div align="center">

**Made with ❤️ by clto**

⭐ Star this repo if you find it helpful! ⭐

</div>
