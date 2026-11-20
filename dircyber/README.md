# 🛡️ DIRCYBER FORENSIC SUITE v5.0
**Next-Level GUI-Based Mobile Digital Forensics Workstation for Kali Linux**

### 🚀 Key Features
- **Live USB Device Monitor:** Real-time detection of connected Android devices via ADB.
- **A-to-Z Mobile Acquisition:** Extracts Hardware Telemetry, Call Logs, SMS/MMS, Contacts, Accounts, Wi-Fi/Bluetooth diagnostics, and App Usage Stats.
- **Live Forensic Screenshot Capture:** Captures timestamped PNG screenshots with SHA-256 verification.
- **Hidden Media & File Carving:** Recovers `.thumbnails`, WhatsApp `.Statuses`, and carves embedded JPEG/PDF signatures.
- **Interactive GPS Map & HTML Report:** Plots geotagged EXIF photos on an interactive map and generates MD5/SHA-256 chain-of-custody reports.
- **Global Keyword & IOC Search:** Searches phone numbers, URLs, and keywords across all extracted artifacts.

### 🛠️ Installation & Usage (Kali Linux)
```bash
sudo apt update && sudo apt install -y android-tools-adb python3-pyqt6 python3-pil sqlite3
git clone [https://github.com/dircyber/DIRCYBER-Forensic-Suite.git](https://github.com/dircyber/DIRCYBER-Forensic-Suite.git)
cd DIRCYBER-Forensic-Suite
python3 dircyber.py
