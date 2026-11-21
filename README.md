# 🛡️ DIRCYBER FORENSIC SUITE v8.5 — Tactical Edition
**Next-Level GUI-Based Mobile Digital Forensics, Bitstream Imaging & Deep Recovery Workstation for Kali Linux**






⚠️ Legal & Ethical Disclaimer
This tool is developed strictly for authorized digital forensics investigations, academic research, and law enforcement/incident response training. Always obtain proper legal authorization before acquiring or analyzing any mobile device.

Developed by: Kaleem Ullah (DIRCYBER  

---

### 🚀 Key Capabilities & Modules (v8.5)
- **💿 Direct Full Mobile Bitstream Imaging (`.dd`):** Creates full physical (rooted block) or logical bitstream (`.dd`) forensic images directly on Desktop with instant **MD5 & SHA-256** integrity verification reports.
- **🎬🎵 Audio, Video & Corrupt File Deep Recovery:** Integrates **Foremost**, **PhotoRec (TestDisk)**, **SleuthKit (`tsk_recover`)**, and a custom binary header/EOF repair engine to recover deleted or corrupted videos (`.mp4`, `.avi`, `.mov`, `.3gp`), audios (`.mp3`, `.wav`, `.m4a`, `.ogg`), photos (`.jpg`, `.png`), and documents (`.pdf`, `.sqlite`).
- **🚨 Red-Line Tampering & Integrity Detector:** Audits case folders against cryptographic hash baselines and flags any **modified, deleted, untracked, or header-corrupted files in RED**.
- **📋 NIST / ISO 27037 5-Stage Forensic Workflow:**
  1. **Chain of Custody Intake:** Generates formal `00_Chain_of_Custody.txt` with Case ID, Evidence Tag, and Examiner details.
  2. **Preservation & Isolation Check:** Verifies Airplane Mode, Wi-Fi radio, and battery telemetry before acquisition.
  3. **Dual-Hash Logical Acquisition:** Extracts Call Logs, SMS/MMS, Contacts, Accounts, Wi-Fi/Bluetooth diagnostics, App Usage Stats, and Live Screenshots.
  4. **Deep Analysis & Timeline:** Parses SQLite databases, maps geotagged EXIF photos on an interactive Leaflet GPS map, runs spyware permission triage, and builds a chronological timeline.
  5. **Court-Ready HTML & PDF Reporting:** Generates tamper-evident HTML and PDF forensic reports with full SHA-256 verification tables.
- **⚡ Cyber-Tactical Dark GUI:** High-contrast obsidian & neon-cyan command center interface with live USB device detection and Hex/Text artifact inspector.

---

### 🛠️ Installation & Usage (Kali Linux)
```bash
# 1. Install system & forensic dependencies
sudo apt update && sudo apt install -y android-tools-adb python3-pyqt6 python3-pil python3-reportlab sqlite3 foremost sleuthkit testdisk gddrescue

# 2. Clone the repository
git clone [https://github.com/dircyber/DIRCYBER-Forensic-Suite.git](https://github.com/dircyber/DIRCYBER-Forensic-Suite.git)
cd DIRCYBER-Forensic-Suite

# 3. Launch DIRCYBER Forensic Workstation
python3 dircyber.py
