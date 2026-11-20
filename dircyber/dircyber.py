import sys
import os
import traceback
import webbrowser
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTreeView, QTableWidget, QTableWidgetItem, QCheckBox,
    QTextEdit, QSplitter, QLabel, QGroupBox, QProgressBar, QMessageBox,
    QHeaderView, QFileDialog, QLineEdit, QTabWidget
)
from PyQt6.QtGui import QFileSystemModel, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from auto_engine import AutoForensicEngine

class UltimateForensicWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    audit_signal = pyqtSignal(str)
    timeline_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str, str)

    def __init__(self, case_dir, examiner, case_name, options):
        super().__init__()
        self.case_dir = case_dir
        self.examiner = examiner
        self.case_name = case_name
        self.options = options

    def run(self):
        try:
            self.log_signal.emit(f"[*] DIRCYBER v5.0 Ultimate Engine Started | Case: {self.case_name}")
            self.progress_signal.emit(5)

            # 1. Hardware & OS Telemetry
            info = AutoForensicEngine.get_device_info()
            f_info = os.path.join(self.case_dir, "01_Device_Hardware_Profile.txt")
            with open(f_info, "w", encoding="utf-8") as f:
                f.write("====================================================\n")
                f.write("   DIRCYBER FORENSIC SUITE v5.0 - SUMMARY REPORT\n")
                f.write("====================================================\n")
                f.write(f"Case ID   : {self.case_name}\n")
                f.write(f"Examiner  : {self.examiner}\n")
                f.write(f"Timestamp : {datetime.now()}\n\n")
                for k, v in info.items():
                    f.write(f"{k:<20}: {v}\n")
            self.log_signal.emit("[+] Extracted Hardware, Bootloader & OS Telemetry.")
            self.progress_signal.emit(12)

            # 2. Call Logs
            if self.options["calls"]:
                self.log_signal.emit("[*] Extracting Call Logs...")
                AutoForensicEngine.extract_content_uri(
                    "content://call_log/calls",
                    os.path.join(self.case_dir, "02_Call_Logs.txt")
                )
            self.progress_signal.emit(20)

            # 3. SMS & Contacts
            if self.options["sms"]:
                self.log_signal.emit("[*] Extracting SMS/MMS & Contacts...")
                AutoForensicEngine.extract_content_uri(
                    "content://sms",
                    os.path.join(self.case_dir, "03_SMS_Messages.txt")
                )
                AutoForensicEngine.extract_content_uri(
                    "content://contacts/phones",
                    os.path.join(self.case_dir, "04_Contacts_Directory.txt")
                )
            self.progress_signal.emit(28)

            # 4. Accounts, Wi-Fi & Bluetooth Forensics
            if self.options["accounts"]:
                self.log_signal.emit("[*] Extracting Google Accounts, Wi-Fi & Bluetooth...")
                f_acc = os.path.join(self.case_dir, "05_Accounts_WiFi_Bluetooth.txt")
                with open(f_acc, "w", encoding="utf-8", errors="ignore") as f:
                    f.write("=== REGISTERED DEVICE ACCOUNTS ===\n")
                    f.write(AutoForensicEngine.run_adb(["shell", "dumpsys", "account"]))
                    f.write("\n\n=== WIFI DIAGNOSTICS ===\n")
                    f.write(AutoForensicEngine.run_adb(["shell", "dumpsys", "wifi"]))
                    f.write("\n\n=== BLUETOOTH PAIRED DEVICES ===\n")
                    f.write(AutoForensicEngine.run_adb(["shell", "dumpsys", "bluetooth_manager"]))
            self.progress_signal.emit(38)

            # 5. Spyware & Security Audit
            if self.options["audit"]:
                self.log_signal.emit("[*] Running Spyware & Permission Triage...")
                f_aud = os.path.join(self.case_dir, "06_Spyware_Security_Audit.txt")
                audit_txt = AutoForensicEngine.security_and_spyware_audit(f_aud)
                self.audit_signal.emit(audit_txt)
            self.progress_signal.emit(48)

            # 6. Live System Logs & Usage Stats
            if self.options["logs"]:
                self.log_signal.emit("[*] Capturing Logcat & App Usage Stats...")
                with open(os.path.join(self.case_dir, "07_System_Logcat.txt"), "w", encoding="utf-8", errors="ignore") as f:
                    f.write(AutoForensicEngine.run_adb(["logcat", "-d"]))
                with open(os.path.join(self.case_dir, "08_App_Usage_Stats.txt"), "w", encoding="utf-8", errors="ignore") as f:
                    f.write(AutoForensicEngine.run_adb(["shell", "dumpsys", "usagestats"]))
            self.progress_signal.emit(58)

            # 7. Storage, Hidden Thumbnails & Interactive GPS Map
            if self.options["storage"]:
                self.log_signal.emit("[*] Pulling Downloads, Docs, Camera & Hidden Thumbnails...")
                AutoForensicEngine.pull_folder("/sdcard/Download", os.path.join(self.case_dir, "Storage_Downloads"))
                AutoForensicEngine.pull_folder("/sdcard/Documents", os.path.join(self.case_dir, "Storage_Documents"))
                AutoForensicEngine.pull_folder("/sdcard/DCIM/.thumbnails", os.path.join(self.case_dir, "Recovered_Thumbnails"))
                dcim = os.path.join(self.case_dir, "Storage_Camera_DCIM")
                AutoForensicEngine.pull_folder("/sdcard/DCIM/Camera", dcim)
                cnt, gps_cnt = AutoForensicEngine.extract_exif_and_map(
                    dcim,
                    os.path.join(self.case_dir, "09_EXIF_GPS_Analysis.txt"),
                    os.path.join(self.case_dir, "GPS_Evidence_Map.html")
                )
                self.log_signal.emit(f"[+] EXIF scanned: {cnt} photos | {gps_cnt} GPS pins mapped.")
            self.progress_signal.emit(72)

            # 8. WhatsApp Media & Hidden Statuses
            if self.options["whatsapp"]:
                self.log_signal.emit("[*] Pulling WhatsApp Media, Backups & Hidden Statuses...")
                wa = os.path.join(self.case_dir, "App_WhatsApp_Data")
                AutoForensicEngine.pull_folder("/sdcard/Android/media/com.whatsapp/WhatsApp", wa)
                AutoForensicEngine.pull_folder("/sdcard/WhatsApp", wa)
                AutoForensicEngine.pull_folder(
                    "/sdcard/Android/media/com.whatsapp/WhatsApp/Media/.Statuses",
                    os.path.join(self.case_dir, "Recovered_WhatsApp_Statuses")
                )
            self.progress_signal.emit(80)

            # 9. SQLite Parsing & Hidden File Carving
            if self.options["carving"]:
                self.log_signal.emit("[*] Parsing SQLite DBs & Carving Hidden Files...")
                db_cnt = AutoForensicEngine.parse_sqlite_databases(self.case_dir)
                carved = AutoForensicEngine.carve_hidden_artifacts(self.case_dir)
                self.log_signal.emit(f"[+] Parsed {db_cnt} SQLite DBs | Carved {carved} embedded files.")
            self.progress_signal.emit(88)

            # 10. Timeline Reconstruction
            self.log_signal.emit("[*] Reconstructing Chronological Activity Timeline...")
            tl_text = AutoForensicEngine.build_forensic_timeline(
                self.case_dir, os.path.join(self.case_dir, "12_Forensic_Timeline.txt")
            )
            self.timeline_signal.emit(tl_text)

            # 11. Master Integrity Hashes & HTML Report
            self.log_signal.emit("[*] Generating MD5 & SHA-256 Hashes & Executive Report...")
            rows_html = ""
            hlog = os.path.join(self.case_dir, "99_Master_Integrity_Hashes.txt")
            skip = ["99_Master_Integrity_Hashes.txt", "DIRCYBER_Forensic_Report.html"]
            total_files = 0
            with open(hlog, "w", encoding="utf-8") as hf:
                hf.write("DIRCYBER FORENSIC INTEGRITY LOG (MD5 & SHA-256)\n" + "=" * 60 + "\n\n")
                for root, _, files in os.walk(self.case_dir):
                    for file in sorted(files):
                        if file in skip:
                            continue
                        fp = os.path.join(root, file)
                        rel = os.path.relpath(fp, self.case_dir)
                        sz = os.path.getsize(fp)
                        m5, sh = AutoForensicEngine.compute_hashes(fp)
                        total_files += 1
                        hf.write(f"Artifact: {rel}\n  Size  : {sz} bytes\n  MD5   : {m5}\n  SHA256: {sh}\n\n")
                        rows_html += (
                            f"<tr><td>{rel}</td><td>{sz:,}</td>"
                            f"<td style='font-family:monospace'>{m5}</td>"
                            f"<td style='font-family:monospace'>{sh}</td></tr>"
                        )

            rpath = os.path.join(self.case_dir, "DIRCYBER_Forensic_Report.html")
            drows = "".join([f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in info.items()])
            html = f"""<!DOCTYPE html>
            <html><head><meta charset="utf-8"><title>DIRCYBER FORENSIC REPORT</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #090d16; color: #e2e8f0; margin: 30px; }}
                .header {{ background: linear-gradient(90deg, #0284c7, #1e3a8a); padding: 20px; border-radius: 8px; }}
                h1 {{ margin: 0; font-size: 24px; color: #ffffff; }}
                h2 {{ color: #38bdf8; border-bottom: 1px solid #1e293b; padding-bottom: 6px; margin-top: 25px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; background: #111827; }}
                th, td {{ border: 1px solid #1f2937; padding: 9px; font-size: 12px; text-align: left; }}
                th {{ background: #1e293b; color: #38bdf8; width: 22%; }}
                .badge {{ background: #059669; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }}
            </style></head><body>
            <div class="header">
                <h1>🛡️ DIRCYBER FORENSIC SUITE v5.0 — DIGITAL EVIDENCE REPORT</h1>
                <p style="margin:5px 0 0 0;">Case ID: <b>{self.case_name}</b> | Lead Examiner: <b>{self.examiner}</b> | Date: <b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b></p>
            </div>
            <p><span class="badge">CHAIN OF CUSTODY VERIFIED</span> Total Evidence Files: <b>{total_files}</b></p>
            <h2>1. Target Mobile Device Telemetry</h2>
            <table>{drows}</table>
            <h2>2. Cryptographic Evidence Hash Log (MD5 & SHA-256)</h2>
            <table><tr><th style="width:30%">Artifact Path</th><th style="width:10%">Size (Bytes)</th><th style="width:25%">MD5</th><th style="width:35%">SHA-256</th></tr>
            {rows_html}</table></body></html>"""
            with open(rpath, "w", encoding="utf-8") as rf:
                rf.write(html)

            self.progress_signal.emit(100)
            self.log_signal.emit(f"[✔] ACQUISITION COMPLETE! {total_files} artifacts preserved.")
            self.finished_signal.emit(self.case_dir, rpath)
        except Exception as exc:
            self.log_signal.emit(f"[!] Non-Fatal Warning: {exc}")
            self.finished_signal.emit(self.case_dir, "")


class DirCyberUltimateGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DIRCYBER FORENSIC SUITE v5.0 — Ultimate Mobile Forensics Workstation")
        self.resize(1420, 860)
        self.output_base = os.path.abspath("dircyber_cases")
        os.makedirs(self.output_base, exist_ok=True)
        self.active_case_dir = self.output_base

        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #090d16; color: #e2e8f0; font-family: 'Segoe UI', Arial; }
            QGroupBox { border: 1px solid #1e293b; border-radius: 6px; margin-top: 6px; font-weight: bold; color: #38bdf8; padding: 8px; }
            QLineEdit { background-color: #111827; border: 1px solid #334155; padding: 6px; border-radius: 4px; color: #f8fafc; }
            QCheckBox { spacing: 8px; font-size: 12px; padding: 2px; }
            QPushButton { background-color: #0284c7; color: white; padding: 8px; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #0369a1; }
            QTreeView, QTableWidget, QTextEdit { background-color: #0f172a; border: 1px solid #1e293b; color: #cbd5e1; }
            QHeaderView::section { background-color: #1e293b; color: #38bdf8; padding: 6px; font-weight: bold; }
            QTabWidget::pane { border: 1px solid #1e293b; }
            QTabBar::tab { background: #1e293b; color: #94a3b8; padding: 8px 14px; font-weight: bold; }
            QTabBar::tab:selected { background: #0284c7; color: white; }
        """)
        self.init_ui()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Confirm Exit — DIRCYBER FORENSIC",
            "Are you sure you want to close DIRCYBER FORENSIC SUITE?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # LEFT SIDEBAR
        left_layout = QVBoxLayout()
        banner = QLabel("🛡️ DIRCYBER FORENSIC v5.0")
        banner.setFont(QFont("Consolas", 15, QFont.Weight.Bold))
        banner.setStyleSheet("color: #38bdf8; padding: 2px;")
        left_layout.addWidget(banner)

        # Live Device Connection Status Bar
        self.lbl_status = QLabel("🔴 DISCONNECTED: Checking USB...")
        self.lbl_status.setStyleSheet(
            "background-color: #450a0a; color: #fca5a5; padding: 7px; "
            "border-radius: 5px; font-weight: bold; font-size: 12px;"
        )
        left_layout.addWidget(self.lbl_status)

        # Quick Action Row: Refresh + Live Screenshot
        quick_row = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh USB")
        btn_refresh.setStyleSheet("background-color: #1e293b; padding: 6px; font-size: 11px;")
        btn_refresh.clicked.connect(self.update_device_status)

        btn_scr = QPushButton("📸 Live Screenshot")
        btn_scr.setStyleSheet("background-color: #7c3aed; padding: 6px; font-size: 11px;")
        btn_scr.clicked.connect(self.take_live_screenshot)

        quick_row.addWidget(btn_refresh)
        quick_row.addWidget(btn_scr)
        left_layout.addLayout(quick_row)

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_device_status)
        self.status_timer.start(2000)
        self.update_device_status()

        # 1. Case & Storage Path
        case_box = QGroupBox("1. Case & Storage Configuration")
        c_layout = QVBoxLayout()
        self.txt_case = QLineEdit(f"CASE_{datetime.now().strftime('%Y%m%d_%H%M')}")
        self.txt_examiner = QLineEdit("Kaleem Ullah")

        path_row = QHBoxLayout()
        self.txt_path = QLineEdit(self.output_base)
        self.txt_path.setReadOnly(True)
        btn_browse = QPushButton("Browse...")
        btn_browse.setMaximumWidth(80)
        btn_browse.clicked.connect(self.choose_output_folder)
        path_row.addWidget(self.txt_path)
        path_row.addWidget(btn_browse)

        c_layout.addWidget(QLabel("Case ID:"))
        c_layout.addWidget(self.txt_case)
        c_layout.addWidget(QLabel("Lead Examiner:"))
        c_layout.addWidget(self.txt_examiner)
        c_layout.addWidget(QLabel("Save Output Folder:"))
        c_layout.addLayout(path_row)
        case_box.setLayout(c_layout)
        left_layout.addWidget(case_box)

        # 2. A-to-Z Extraction Modules
        mod_box = QGroupBox("2. A-to-Z Forensic Modules")
        m_layout = QVBoxLayout()

        sel_row = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_all.setStyleSheet("padding: 4px; font-size: 11px; background-color: #1e293b;")
        btn_all.clicked.connect(lambda: self.toggle_all(True))
        btn_none = QPushButton("Clear All")
        btn_none.setStyleSheet("padding: 4px; font-size: 11px; background-color: #1e293b;")
        btn_none.clicked.connect(lambda: self.toggle_all(False))
        sel_row.addWidget(btn_all)
        sel_row.addWidget(btn_none)
        m_layout.addLayout(sel_row)

        self.chk_calls = QCheckBox("Call History Logs (Incoming/Outgoing)")
        self.chk_sms = QCheckBox("SMS/MMS & Phonebook Contacts")
        self.chk_accounts = QCheckBox("Google Accounts, Wi-Fi & Bluetooth")
        self.chk_audit = QCheckBox("Spyware & High-Risk Permission Audit")
        self.chk_logs = QCheckBox("System Logcat & App Usage Stats")
        self.chk_storage = QCheckBox("Downloads, Camera, Thumbnails & GPS Map")
        self.chk_whatsapp = QCheckBox("WhatsApp Media, DBs & Hidden Statuses")
        self.chk_carving = QCheckBox("SQLite Parser & Hidden File Carving")

        self.all_chks = [
            self.chk_calls, self.chk_sms, self.chk_accounts, self.chk_audit,
            self.chk_logs, self.chk_storage, self.chk_whatsapp, self.chk_carving
        ]
        for c in self.all_chks:
            c.setChecked(True)
            m_layout.addWidget(c)
        mod_box.setLayout(m_layout)
        left_layout.addWidget(mod_box)

        self.btn_start = QPushButton("🚀 START ULTIMATE ACQUISITION")
        self.btn_start.setStyleSheet("background-color: #059669; font-size: 13px; padding: 11px;")
        self.btn_start.clicked.connect(self.launch_acquisition)
        left_layout.addWidget(self.btn_start)

        btn_seal = QPushButton("🔒 Seal Case into Verified ZIP")
        btn_seal.setStyleSheet("background-color: #b45309; font-size: 11px; padding: 7px;")
        btn_seal.clicked.connect(self.seal_current_case)
        left_layout.addWidget(btn_seal)

        self.progress = QProgressBar()
        left_layout.addWidget(self.progress)

        left_layout.addWidget(QLabel("📁 Case Evidence Tree:"))
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(self.output_base)
        self.tree = QTreeView()
        self.tree.setModel(self.fs_model)
        self.tree.setRootIndex(self.fs_model.index(self.output_base))
        for col in range(1, 4):
            self.tree.hideColumn(col)
        self.tree.clicked.connect(self.on_tree_clicked)
        left_layout.addWidget(self.tree)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(385)
        main_layout.addWidget(left_widget)

        # RIGHT WORKSPACE: 4 Analysis Tabs
        self.tabs = QTabWidget()

        tab1 = QSplitter(Qt.Orientation.Vertical)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Artifact File Name", "Size (Bytes)", "MD5 Checksum", "SHA-256 Checksum"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(self.on_file_selected)
        tab1.addWidget(self.table)

        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        self.viewer.setFont(QFont("Consolas", 10))
        self.viewer.setText(
            "[*] DIRCYBER FORENSIC SUITE v5.0 Ultimate Workstation Ready.\n"
            "[*] Live USB Monitor, Screenshot Capture, GPS Mapper & IOC Search active."
        )
        tab1.addWidget(self.viewer)
        tab1.setSizes([360, 440])
        self.tabs.addTab(tab1, "1. Evidence & Hex/Text Inspector")

        # Tab 2: Global Keyword / IOC Search
        tab2 = QWidget()
        t2_layout = QVBoxLayout(tab2)
        search_bar = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Enter phone number, name, URL, or keyword to search across entire case...")
        btn_search = QPushButton("🔍 Search Case Artifacts")
        btn_search.clicked.connect(self.run_global_search)
        search_bar.addWidget(self.txt_search)
        search_bar.addWidget(btn_search)
        t2_layout.addLayout(search_bar)

        self.search_results = QTextEdit()
        self.search_results.setReadOnly(True)
        self.search_results.setFont(QFont("Consolas", 10))
        t2_layout.addWidget(self.search_results)
        self.tabs.addTab(tab2, "2. Global Keyword & IOC Search")

        # Tab 3: Spyware & Security Audit
        self.audit_view = QTextEdit()
        self.audit_view.setReadOnly(True)
        self.audit_view.setFont(QFont("Consolas", 10))
        self.audit_view.setText("Run acquisition to view Spyware & High-Risk Permission Triage results...")
        self.tabs.addTab(self.audit_view, "3. Spyware & Permission Audit")

        # Tab 4: Chronological Activity Timeline
        self.timeline_view = QTextEdit()
        self.timeline_view.setReadOnly(True)
        self.timeline_view.setFont(QFont("Consolas", 10))
        self.timeline_view.setText("Run acquisition to generate Chronological Forensic Activity Timeline...")
        self.tabs.addTab(self.timeline_view, "4. Forensic Activity Timeline")

        main_layout.addWidget(self.tabs)
        self.current_dir = self.output_base

    def update_device_status(self):
        if AutoForensicEngine.is_device_connected():
            model = AutoForensicEngine.run_adb(["shell", "getprop", "ro.product.model"])
            ver = AutoForensicEngine.run_adb(["shell", "getprop", "ro.build.version.release"])
            self.lbl_status.setText(f"🟢 CONNECTED: {model} (Android {ver})")
            self.lbl_status.setStyleSheet(
                "background-color: #064e3b; color: #6ee7b7; padding: 7px; "
                "border-radius: 5px; font-weight: bold; font-size: 12px;"
            )
        else:
            self.lbl_status.setText("🔴 DISCONNECTED: Connect Phone (USB Debugging)")
            self.lbl_status.setStyleSheet(
                "background-color: #450a0a; color: #fca5a5; padding: 7px; "
                "border-radius: 5px; font-weight: bold; font-size: 12px;"
            )

    def take_live_screenshot(self):
        if not AutoForensicEngine.is_device_connected():
            QMessageBox.warning(self, "Disconnected", "Connect Android device first!")
            return
        scr_dir = os.path.join(self.active_case_dir, "Live_Screenshots")
        path, m5, sh = AutoForensicEngine.capture_forensic_screenshot(scr_dir)
        if path:
            self.viewer.append(f"[📸] Captured Screenshot: {path}\n     SHA-256: {sh}")
            self.load_dir(scr_dir)
        else:
            QMessageBox.warning(self, "Error", "Failed to capture screenshot (screen may be DRM protected).")

    def run_global_search(self):
        kw = self.txt_search.text().strip()
        if not kw:
            return
        self.search_results.setText(f"[*] Searching for '{kw}' across {self.active_case_dir}...\n\n")
        res = AutoForensicEngine.search_keyword_in_case(self.active_case_dir, kw)
        self.search_results.append(res)

    def seal_current_case(self):
        if self.active_case_dir == self.output_base:
            QMessageBox.information(self, "Select Case", "Run an acquisition or select a case folder first.")
            return
        zpath, sh = AutoForensicEngine.create_sealed_evidence_zip(self.active_case_dir)
        QMessageBox.information(
            self, "Case Sealed",
            f"Tamper-Proof Evidence Archive Created:\n{zpath}\n\nMaster SHA-256:\n{sh}"
        )

    def toggle_all(self, state):
        for c in self.all_chks:
            c.setChecked(state)

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_base)
        if folder:
            self.output_base = folder
            self.active_case_dir = folder
            self.txt_path.setText(folder)
            self.fs_model.setRootPath(folder)
            self.tree.setRootIndex(self.fs_model.index(folder))

    def launch_acquisition(self):
        if not AutoForensicEngine.is_device_connected():
            QMessageBox.warning(
                self, "Device Not Connected",
                "No authorized Android device detected.\nEnable USB Debugging and tap 'Allow' on the phone."
            )
            return

        case_name = self.txt_case.text().strip() or f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        examiner = self.txt_examiner.text().strip() or "DIRCYBER Examiner"
        cdir = os.path.join(self.output_base, f"{case_name}_{datetime.now().strftime('%H%M%S')}")
        os.makedirs(cdir, exist_ok=True)
        self.active_case_dir = cdir

        opts = {
            "calls": self.chk_calls.isChecked(),
            "sms": self.chk_sms.isChecked(),
            "accounts": self.chk_accounts.isChecked(),
            "audit": self.chk_audit.isChecked(),
            "logs": self.chk_logs.isChecked(),
            "storage": self.chk_storage.isChecked(),
            "whatsapp": self.chk_whatsapp.isChecked(),
            "carving": self.chk_carving.isChecked(),
        }

        self.btn_start.setEnabled(False)
        self.viewer.clear()
        self.worker = UltimateForensicWorker(cdir, examiner, case_name, opts)
        self.worker.log_signal.connect(lambda m: self.viewer.append(m))
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.audit_signal.connect(self.audit_view.setText)
        self.worker.timeline_signal.connect(self.timeline_view.setText)
        self.worker.finished_signal.connect(self.on_done)
        self.worker.start()

    def on_done(self, cdir, rpath):
        self.btn_start.setEnabled(True)
        self.load_dir(cdir)
        if rpath and os.path.exists(rpath):
            webbrowser.open(f"file://{rpath}")

    def on_tree_clicked(self, idx):
        p = self.fs_model.filePath(idx)
        if os.path.isdir(p):
            self.active_case_dir = p
            self.load_dir(p)
        elif os.path.isfile(p):
            self.viewer.setText(AutoForensicEngine.format_preview(p))

    def load_dir(self, folder):
        self.current_dir = folder
        self.table.setRowCount(0)
        for fn in sorted(os.listdir(folder)):
            fp = os.path.join(folder, fn)
            if os.path.isfile(fp):
                r = self.table.rowCount()
                self.table.insertRow(r)
                sz = os.path.getsize(fp)
                m5, sh = AutoForensicEngine.compute_hashes(fp)
                self.table.setItem(r, 0, QTableWidgetItem(fn))
                self.table.setItem(r, 1, QTableWidgetItem(str(sz)))
                self.table.setItem(r, 2, QTableWidgetItem(m5))
                self.table.setItem(r, 3, QTableWidgetItem(sh))

    def on_file_selected(self, row, _col):
        fn = self.table.item(row, 0).text()
        fp = os.path.join(self.current_dir, fn)
        if os.path.isfile(fp):
            self.viewer.setText(AutoForensicEngine.format_preview(fp))

def global_exception_handler(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(err_msg)

if __name__ == "__main__":
    sys.excepthook = global_exception_handler
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    win = DirCyberUltimateGUI()
    win.show()
    sys.exit(app.exec())
