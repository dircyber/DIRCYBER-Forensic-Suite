import sys
import os
import traceback
import webbrowser
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTreeView, QTableWidget, QTableWidgetItem, QCheckBox,
    QTextEdit, QSplitter, QLabel, QGroupBox, QProgressBar, QMessageBox,
    QHeaderView, QFileDialog, QLineEdit, QTabWidget, QScrollArea, QFrame
)
from PyQt6.QtGui import QFileSystemModel, QFont, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from auto_engine import AutoForensicEngine

# =====================================================================
#  NEXT-LEVEL CYBER-FORENSICS TACTICAL QSS STYLESHEET (DIRCYBER EDITION)
# =====================================================================
DIRCYBER_TACTICAL_QSS = """
QMainWindow, QWidget {
    background-color: #050811;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Ubuntu', Arial, sans-serif;
    font-size: 12px;
}

/* Header Banner Frame */
QFrame#HeaderBanner {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #071324, stop:0.5 #0c2340, stop:1 #050811);
    border: 1px solid #00f0ff;
    border-radius: 8px;
    padding: 6px;
}

/* Group Boxes with Neon Cyber Borders */
QGroupBox {
    background-color: #090f1d;
    border: 1px solid #1e3a5f;
    border-top: 2px solid #00f0ff;
    border-radius: 6px;
    margin-top: 10px;
    padding: 10px 8px 8px 8px;
    font-weight: bold;
    color: #00f0ff;
    font-size: 11px;
    text-transform: uppercase;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    background-color: #050811;
    color: #00f0ff;
    letter-spacing: 1px;
}

/* Input Fields */
QLineEdit {
    background-color: #04070f;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
    padding: 6px;
    color: #38bdf8;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
}
QLineEdit:focus {
    border: 1px solid #00f0ff;
    background-color: #081226;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #cbd5e1;
    padding: 3px;
    font-size: 11px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid #00f0ff;
    background-color: #04070f;
}
QCheckBox::indicator:checked {
    background-color: #00f0ff;
    border: 1px solid #ffffff;
}

/* Tactical Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #0369a1);
    color: #ffffff;
    border: 1px solid #38bdf8;
    border-radius: 5px;
    padding: 8px 10px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f0ff, stop:1 #0284c7);
    color: #020617;
    border: 1px solid #ffffff;
}
QPushButton:disabled {
    background-color: #1e293b;
    color: #64748b;
    border: 1px solid #334155;
}

/* Special Action Buttons */
QPushButton#BtnImage {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #2563eb);
    border: 1px solid #60a5fa;
}
QPushButton#BtnImage:hover {
    background: #3b82f6;
    color: white;
}
QPushButton#BtnRecover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b45309, stop:1 #d97706);
    border: 1px solid #fbbf24;
}
QPushButton#BtnRecover:hover {
    background: #f59e0b;
    color: #020617;
}
QPushButton#BtnTamper {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #991b1b, stop:1 #dc2626);
    border: 1px solid #f87171;
}
QPushButton#BtnTamper:hover {
    background: #ef4444;
    color: white;
}
QPushButton#BtnExecute {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #059669);
    border: 1px solid #34d399;
    font-size: 12px;
    padding: 11px;
}
QPushButton#BtnExecute:hover {
    background: #10b981;
    color: #020617;
}

/* Progress Bar */
QProgressBar {
    background-color: #04070f;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #00f0ff);
    border-radius: 3px;
}

/* Data Tables, Tree & Console Terminal */
QTableWidget, QTreeView {
    background-color: #070c18;
    alternate-background-color: #0b1326;
    border: 1px solid #1e3a5f;
    gridline-color: #162842;
    color: #e2e8f0;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}
QHeaderView::section {
    background-color: #0c192e;
    color: #00f0ff;
    border: 1px solid #1e3a5f;
    padding: 7px;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 11px;
}
QTextEdit {
    background-color: #03060c;
    border: 1px solid #1e3a5f;
    color: #38bdf8;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    padding: 6px;
}

/* Navigation Tabs */
QTabWidget::pane {
    border: 1px solid #1e3a5f;
    background-color: #050811;
}
QTabBar::tab {
    background-color: #091224;
    color: #94a3b8;
    border: 1px solid #1e3a5f;
    border-bottom: none;
    padding: 9px 16px;
    margin-right: 2px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    font-weight: bold;
}
QTabBar::tab:selected {
    background-color: #0c2340;
    color: #00f0ff;
    border-top: 2px solid #00f0ff;
}
QTabBar::tab:hover {
    color: #ffffff;
}

/* Sleek Dark Scrollbars */
QScrollBar:vertical {
    background: #050811;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #1e3a5f;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #00f0ff;
}
"""


class ImageCreationWorker(QThread):
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(str, str)

    def __init__(self, dest_folder, case_name):
        super().__init__()
        self.dest = dest_folder
        self.case = case_name

    def run(self):
        try:
            self.log_signal.emit(f"[*] Creating Full Mobile Forensic Image (.dd) on Desktop: {self.dest} ...")
            img_p, rep_p, sz, m5, sh = AutoForensicEngine.create_full_mobile_image(
                self.dest, self.case, self.log_signal.emit
            )
            self.log_signal.emit(f"[✔] FULL IMAGE CREATED: {img_p} ({sz:,} bytes)")
            self.log_signal.emit(f"    MD5   : {m5}")
            self.log_signal.emit(f"    SHA256: {sh}")
            self.log_signal.emit(f"[✔] IMAGE REPORT SAVED: {rep_p}")
            self.done_signal.emit(img_p, rep_p)
        except Exception as e:
            self.log_signal.emit(f"[!] Image Creation Error: {e}")
            self.done_signal.emit("", "")


class DeepRecoveryWorker(QThread):
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(str, int)

    def __init__(self, image_path, out_dir):
        super().__init__()
        self.img = image_path
        self.out = out_dir

    def run(self):
        try:
            self.log_signal.emit(f"[*] Starting Video, Audio, Photo & Corrupt Data Recovery on: {self.img}")
            rec_dir, count = AutoForensicEngine.deep_recover_media_and_files(
                self.img, self.out, self.log_signal.emit
            )
            self.log_signal.emit(f"[✔] RECOVERY COMPLETE! {count} Video/Audio/Media files recovered in: {rec_dir}")
            self.done_signal.emit(rec_dir, count)
        except Exception as e:
            self.log_signal.emit(f"[!] Recovery Error: {e}")
            self.done_signal.emit("", 0)


class CompleteWorkflowWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    audit_signal = pyqtSignal(str)
    timeline_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str, str, str)

    def __init__(self, case_dir, intake_data, options):
        super().__init__()
        self.case_dir = case_dir
        self.intake = intake_data
        self.options = options

    def run(self):
        try:
            self.log_signal.emit(f"[*] STAGE 1: Generating Chain of Custody ({self.intake['evidence_tag']})...")
            AutoForensicEngine.generate_chain_of_custody(self.case_dir, self.intake)
            self.progress_signal.emit(8)

            self.log_signal.emit("[*] STAGE 2: Checking Network Isolation & Battery State...")
            iso_info = AutoForensicEngine.check_isolation_state()
            self.progress_signal.emit(15)

            self.log_signal.emit("[*] STAGE 3: Extracting Hardware & OS Telemetry...")
            info = AutoForensicEngine.get_device_info()
            with open(os.path.join(self.case_dir, "01_Device_Hardware_Profile.txt"), "w", encoding="utf-8") as f:
                for k, v in {**iso_info, **info}.items():
                    f.write(f"{k:<20}: {v}\n")
            self.progress_signal.emit(25)

            if self.options["calls"]:
                AutoForensicEngine.extract_content_uri("content://call_log/calls", os.path.join(self.case_dir, "02_Call_Logs.txt"))
            if self.options["sms"]:
                AutoForensicEngine.extract_content_uri("content://sms", os.path.join(self.case_dir, "03_SMS_Messages.txt"))
                AutoForensicEngine.extract_content_uri("content://contacts/phones", os.path.join(self.case_dir, "04_Contacts_Directory.txt"))
            self.progress_signal.emit(40)

            if self.options["audit"]:
                audit_txt = AutoForensicEngine.security_and_spyware_audit(os.path.join(self.case_dir, "06_Spyware_Security_Audit.txt"))
                self.audit_signal.emit(audit_txt)
            self.progress_signal.emit(55)

            if self.options["storage"]:
                AutoForensicEngine.pull_folder("/sdcard/Download", os.path.join(self.case_dir, "Storage_Downloads"))
                AutoForensicEngine.pull_folder("/sdcard/Documents", os.path.join(self.case_dir, "Storage_Documents"))
                AutoForensicEngine.pull_folder("/sdcard/DCIM/.thumbnails", os.path.join(self.case_dir, "Recovered_Thumbnails"))
                dcim = os.path.join(self.case_dir, "Storage_Camera_DCIM")
                AutoForensicEngine.pull_folder("/sdcard/DCIM/Camera", dcim)
                AutoForensicEngine.extract_exif_and_map(
                    dcim,
                    os.path.join(self.case_dir, "09_EXIF_GPS_Analysis.txt"),
                    os.path.join(self.case_dir, "GPS_Evidence_Map.html")
                )
            self.progress_signal.emit(75)

            if self.options["whatsapp"]:
                wa = os.path.join(self.case_dir, "App_WhatsApp_Data")
                AutoForensicEngine.pull_folder("/sdcard/Android/media/com.whatsapp/WhatsApp", wa)
                AutoForensicEngine.pull_folder("/sdcard/WhatsApp", wa)
            self.progress_signal.emit(82)

            AutoForensicEngine.parse_sqlite_databases(self.case_dir)
            tl_text = AutoForensicEngine.build_forensic_timeline(
                self.case_dir, os.path.join(self.case_dir, "12_Forensic_Timeline.txt")
            )
            self.timeline_signal.emit(tl_text)

            rows_html = ""
            hash_records = []
            hlog = os.path.join(self.case_dir, "99_Master_Integrity_Hashes.txt")
            skip = ["99_Master_Integrity_Hashes.txt", "DIRCYBER_Forensic_Report.html", "DIRCYBER_Forensic_Report.pdf"]

            with open(hlog, "w", encoding="utf-8") as hf:
                for root, _, files in os.walk(self.case_dir):
                    for file in sorted(files):
                        if file in skip:
                            continue
                        fp = os.path.join(root, file)
                        rel = os.path.relpath(fp, self.case_dir)
                        sz = os.path.getsize(fp)
                        m5, sh = AutoForensicEngine.compute_hashes(fp)
                        hash_records.append((rel, sz, m5, sh))
                        hf.write(f"Artifact: {rel}\n  Size  : {sz} bytes\n  MD5   : {m5}\n  SHA256: {sh}\n\n")
                        rows_html += f"<tr><td>{rel}</td><td>{sz:,}</td><td>{m5}</td><td>{sh}</td></tr>"

            rpath = os.path.join(self.case_dir, "DIRCYBER_Forensic_Report.html")
            drows = "".join([f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in {**iso_info, **info}.items()])
            html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>DIRCYBER REPORT</title>
            <style>body{{font-family:Arial;background:#050811;color:#e2e8f0;margin:25px;}}
            table{{width:100%;border-collapse:collapse;background:#090f1d;}}
            th,td{{border:1px solid #1e3a5f;padding:8px;font-size:12px;text-align:left;}}
            th{{background:#0c2340;color:#00f0ff;}}</style></head><body>
            <h1>🛡️ DIRCYBER FORENSIC SUITE v8.5 — DIGITAL EVIDENCE REPORT</h1>
            <table>{drows}</table><h2>Evidence Hashes</h2>
            <table><tr><th>Artifact</th><th>Bytes</th><th>MD5</th><th>SHA-256</th></tr>{rows_html}</table></body></html>"""
            with open(rpath, "w", encoding="utf-8") as rf:
                rf.write(html)

            pdf_path = os.path.join(self.case_dir, "DIRCYBER_Forensic_Report.pdf")
            AutoForensicEngine.generate_pdf_report(pdf_path, self.intake, info, iso_info, hash_records)

            self.progress_signal.emit(100)
            self.log_signal.emit("[✔] 5-STAGE WORKFLOW COMPLETE!")
            self.finished_signal.emit(self.case_dir, rpath, pdf_path)
        except Exception as exc:
            self.log_signal.emit(f"[!] Warning: {exc}")
            self.finished_signal.emit(self.case_dir, "", "")


class DirCyberTacticalGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DIRCYBER FORENSIC SUITE v8.5 — Tactical Cyber-Forensics Command Center")
        self.resize(1480, 900)
        desktop_path = os.path.expanduser("~/Desktop")
        self.output_base = desktop_path if os.path.isdir(desktop_path) else os.path.abspath("dircyber_cases")
        self.active_case_dir = self.output_base
        self.setStyleSheet(DIRCYBER_TACTICAL_QSS)
        self.init_ui()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Confirm Exit", "Terminate DIRCYBER FORENSIC WORKSTATION?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        event.accept() if reply == QMessageBox.StandardButton.Yes else event.ignore()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_vbox = QVBoxLayout(central)
        root_vbox.setContentsMargins(8, 8, 8, 8)
        root_vbox.setSpacing(8)

        # TOP TACTICAL HEADER BANNER
        header_frame = QFrame()
        header_frame.setObjectName("HeaderBanner")
        h_layout = QHBoxLayout(header_frame)

        title_box = QVBoxLayout()
        lbl_title = QLabel("⚡ DIRCYBER FORENSIC SUITE // v8.5 TACTICAL EDITION")
        lbl_title.setFont(QFont("Consolas", 15, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #00f0ff; letter-spacing: 1.5px;")
        lbl_sub = QLabel("MOBILE DIGITAL FORENSICS • FULL BITSTREAM IMAGING • AUDIO/VIDEO DEEP CARVING • RED-LINE TAMPER AUDIT")
        lbl_sub.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        h_layout.addLayout(title_box)

        h_layout.addStretch()

        self.lbl_status = QLabel("🔴 TARGET OFFLINE // CONNECT USB")
        self.lbl_status.setStyleSheet(
            "background-color: #3b0712; color: #fda4af; border: 1px solid #f43f5e; "
            "padding: 8px 14px; border-radius: 5px; font-family: 'Consolas'; font-weight: bold; font-size: 12px;"
        )
        h_layout.addWidget(self.lbl_status)
        root_vbox.addWidget(header_frame)

        # MAIN WORKSPACE SPLITTER
        main_layout = QHBoxLayout()
        root_vbox.addLayout(main_layout)

        left_content = QWidget()
        left_layout = QVBoxLayout(left_content)
        left_layout.setContentsMargins(2, 2, 2, 2)

        quick_row = QHBoxLayout()
        btn_refresh = QPushButton("🔄 SCAN USB")
        btn_refresh.clicked.connect(self.update_device_status)
        btn_scr = QPushButton("📸 SCREENSHOT")
        btn_scr.clicked.connect(self.take_live_screenshot)
        quick_row.addWidget(btn_refresh)
        quick_row.addWidget(btn_scr)
        left_layout.addLayout(quick_row)

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_device_status)
        self.status_timer.start(2000)
        self.update_device_status()

        # Full Mobile Image + Audio/Video Recovery
        img_box = QGroupBox("💿 Full Mobile Image & Deep Recovery")
        i_layout = QVBoxLayout()

        self.btn_make_img = QPushButton("💿 CREATE FULL MOBILE IMAGE (.DD)")
        self.btn_make_img.setObjectName("BtnImage")
        self.btn_make_img.clicked.connect(self.start_direct_imaging)
        i_layout.addWidget(self.btn_make_img)

        self.btn_recover_img = QPushButton("🎬🎵 RECOVER VIDEO, AUDIO & CORRUPT")
        self.btn_recover_img.setObjectName("BtnRecover")
        self.btn_recover_img.clicked.connect(self.start_image_recovery)
        i_layout.addWidget(self.btn_recover_img)

        self.btn_tamper_scan = QPushButton("🚨 RED-LINE TAMPER & HASH AUDIT")
        self.btn_tamper_scan.setObjectName("BtnTamper")
        self.btn_tamper_scan.clicked.connect(self.run_tamper_audit)
        i_layout.addWidget(self.btn_tamper_scan)

        img_box.setLayout(i_layout)
        left_layout.addWidget(img_box)

        # Case & Output Storage
        coc_box = QGroupBox("📁 Case & Output Storage (Desktop)")
        c_layout = QVBoxLayout()
        self.txt_case = QLineEdit(f"CASE_{datetime.now().strftime('%Y%m%d_%H%M')}")
        self.txt_tag = QLineEdit(f"EVID-{datetime.now().strftime('%H%M%S')}")
        self.txt_examiner = QLineEdit("Kaleem Ullah")
        self.txt_location = QLineEdit("DIRCYBER Forensics Lab")
        self.txt_condition = QLineEdit("Powered On / Unlocked")

        path_row = QHBoxLayout()
        self.txt_path = QLineEdit(self.output_base)
        self.txt_path.setReadOnly(True)
        btn_browse = QPushButton("...")
        btn_browse.setMaximumWidth(40)
        btn_browse.clicked.connect(self.choose_output_folder)
        path_row.addWidget(self.txt_path)
        path_row.addWidget(btn_browse)

        for lbl, w in [
            ("Case ID:", self.txt_case),
            ("Evidence Tag:", self.txt_tag),
            ("Lead Examiner:", self.txt_examiner),
            ("Save Directory:", None)
        ]:
            c_layout.addWidget(QLabel(lbl))
            if w:
                c_layout.addWidget(w)
        c_layout.addLayout(path_row)
        coc_box.setLayout(c_layout)
        left_layout.addWidget(coc_box)

        # Modules
        mod_box = QGroupBox("⚙️ Acquisition & Analysis Modules")
        m_layout = QVBoxLayout()
        self.chk_calls = QCheckBox("Call History Logs")
        self.chk_sms = QCheckBox("SMS/MMS & Contacts")
        self.chk_audit = QCheckBox("Spyware & Permission Audit")
        self.chk_storage = QCheckBox("Docs, Camera, Thumbnails & GPS")
        self.chk_whatsapp = QCheckBox("WhatsApp Media & Local DBs")

        for c in [self.chk_calls, self.chk_sms, self.chk_audit, self.chk_storage, self.chk_whatsapp]:
            c.setChecked(True)
            m_layout.addWidget(c)
        mod_box.setLayout(m_layout)
        left_layout.addWidget(mod_box)

        self.btn_start = QPushButton("🚀 EXECUTE 5-STAGE WORKFLOW")
        self.btn_start.setObjectName("BtnExecute")
        self.btn_start.clicked.connect(self.launch_acquisition)
        left_layout.addWidget(self.btn_start)

        self.progress = QProgressBar()
        left_layout.addWidget(self.progress)

        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(self.output_base)
        self.tree = QTreeView()
        self.tree.setModel(self.fs_model)
        self.tree.setRootIndex(self.fs_model.index(self.output_base))
        self.tree.setMinimumHeight(130)
        for col in range(1, 4):
            self.tree.hideColumn(col)
        self.tree.clicked.connect(self.on_tree_clicked)
        left_layout.addWidget(self.tree)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(left_content)
        scroll.setMaximumWidth(390)
        main_layout.addWidget(scroll)

        # RIGHT WORKSPACE TABS
        self.tabs = QTabWidget()

        tab1 = QSplitter(Qt.Orientation.Vertical)
        self.table = QTableWidget(0, 5)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeaderLabels([
            "Artifact File Name", "Size (Bytes)", "Integrity / Tamper Status", "MD5 Checksum", "SHA-256 Checksum"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(self.on_file_selected)
        tab1.addWidget(self.table)

        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        self.viewer.setText(
            "================================================================================\n"
            "  DIRCYBER FORENSIC WORKSTATION v8.5 // TACTICAL CYBER-FORENSICS CONSOLE\n"
            "================================================================================\n"
            "[*] SYSTEM READY. Default Evidence Output Path: Desktop\n"
            "[*] [CREATE FULL MOBILE IMAGE] -> Dumps full mobile .dd image & generates hash report.\n"
            "[*] [RECOVER VIDEO, AUDIO]    -> Carves deleted MP4, AVI, MP3, WAV, M4A & corrupt files.\n"
            "[*] [RED-LINE TAMPER AUDIT]   -> Flags modified, deleted, or corrupt files in RED.\n"
        )
        tab1.addWidget(self.viewer)
        tab1.setSizes([380, 440])
        self.tabs.addTab(tab1, "1. RED-LINE INTEGRITY & HEX CONSOLE")

        tab2 = QWidget()
        t2_layout = QVBoxLayout(tab2)
        search_bar = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Enter phone number, keyword, IMEI, or URL to search across entire case...")
        btn_search = QPushButton("🔍 SEARCH CASE")
        btn_search.clicked.connect(self.run_global_search)
        search_bar.addWidget(self.txt_search)
        search_bar.addWidget(btn_search)
        t2_layout.addLayout(search_bar)
        self.search_results = QTextEdit()
        self.search_results.setReadOnly(True)
        t2_layout.addWidget(self.search_results)
        self.tabs.addTab(tab2, "2. GLOBAL IOC & KEYWORD SEARCH")

        self.audit_view = QTextEdit()
        self.audit_view.setReadOnly(True)
        self.tabs.addTab(self.audit_view, "3. SPYWARE & PERMISSION TRIAGE")

        self.timeline_view = QTextEdit()
        self.timeline_view.setReadOnly(True)
        self.tabs.addTab(self.timeline_view, "4. CHRONOLOGICAL TIMELINE")

        main_layout.addWidget(self.tabs)
        self.current_dir = self.output_base

    def start_direct_imaging(self):
        if not AutoForensicEngine.is_device_connected():
            QMessageBox.warning(self, "Target Offline", "Connect Android device via USB Debugging first!")
            return
        case_name = self.txt_case.text().strip() or "DIRCYBER_CASE"
        self.btn_make_img.setEnabled(False)
        self.viewer.clear()
        self.img_worker = ImageCreationWorker(self.output_base, case_name)
        self.img_worker.log_signal.connect(lambda m: self.viewer.append(m))
        self.img_worker.done_signal.connect(self.on_image_created)
        self.img_worker.start()

    def on_image_created(self, img_path, rep_path):
        self.btn_make_img.setEnabled(True)
        if img_path:
            self.load_dir_with_tamper_check(self.output_base)
            if rep_path and os.path.exists(rep_path):
                self.viewer.append("\n" + AutoForensicEngine.format_preview(rep_path))

    def start_image_recovery(self):
        img_file, _ = QFileDialog.getOpenFileName(
            self, "Select Full Mobile Image (.dd / .img) for Video/Audio & File Recovery",
            self.output_base, "Forensic Images (*.dd *.img *.raw *.bin);;All Files (*)"
        )
        if not img_file:
            return
        self.btn_recover_img.setEnabled(False)
        self.viewer.clear()
        self.rec_worker = DeepRecoveryWorker(img_file, self.output_base)
        self.rec_worker.log_signal.connect(lambda m: self.viewer.append(m))
        self.rec_worker.done_signal.connect(self.on_recovery_done)
        self.rec_worker.start()

    def on_recovery_done(self, rec_dir, count):
        self.btn_recover_img.setEnabled(True)
        if rec_dir and os.path.exists(rec_dir):
            self.active_case_dir = rec_dir
            self.load_dir_with_tamper_check(rec_dir)
            QMessageBox.information(
                self, "Deep Recovery Complete",
                f"Recovered {count} Video, Audio, Photo & Corrupt files!\nSaved in:\n{rec_dir}"
            )

    def run_tamper_audit(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Audit for Red-Line Tampering", self.active_case_dir)
        if folder:
            self.load_dir_with_tamper_check(folder)

    def load_dir_with_tamper_check(self, folder):
        self.current_dir = folder
        self.table.setRowCount(0)
        records = AutoForensicEngine.inspect_and_detect_tampering(folder)
        alerts = 0
        for rel, sz, status, m5, sh, is_alert in records:
            r = self.table.rowCount()
            self.table.insertRow(r)
            items = [
                QTableWidgetItem(rel),
                QTableWidgetItem(str(sz)),
                QTableWidgetItem(status),
                QTableWidgetItem(m5),
                QTableWidgetItem(sh),
            ]
            if is_alert:
                alerts += 1
                red_bg = QColor("#7f1d1d")
                white_fg = QColor("#fecaca")
                for it in items:
                    it.setBackground(red_bg)
                    it.setForeground(white_fg)
            else:
                items[2].setForeground(QColor("#34d399"))

            for col_i, it in enumerate(items):
                self.table.setItem(r, col_i, it)

        self.viewer.append(f"[*] Integrity Audit on {folder}: {len(records)} files scanned | {alerts} RED-LINE ALERTS.")

    def update_device_status(self):
        if AutoForensicEngine.is_device_connected():
            model = AutoForensicEngine.run_adb(["shell", "getprop", "ro.product.model"])
            ver = AutoForensicEngine.run_adb(["shell", "getprop", "ro.build.version.release"])
            self.lbl_status.setText(f"🟢 TARGET ONLINE // {model} (Android {ver})")
            self.lbl_status.setStyleSheet(
                "background-color: #022c22; color: #34d399; border: 1px solid #10b981; "
                "padding: 8px 14px; border-radius: 5px; font-family: 'Consolas'; font-weight: bold; font-size: 12px;"
            )
        else:
            self.lbl_status.setText("🔴 TARGET OFFLINE // CONNECT USB")
            self.lbl_status.setStyleSheet(
                "background-color: #3b0712; color: #fda4af; border: 1px solid #f43f5e; "
                "padding: 8px 14px; border-radius: 5px; font-family: 'Consolas'; font-weight: bold; font-size: 12px;"
            )

    def take_live_screenshot(self):
        if not AutoForensicEngine.is_device_connected():
            QMessageBox.warning(self, "Target Offline", "Connect Android device first!")
            return
        scr_dir = os.path.join(self.active_case_dir, "Live_Screenshots")
        path, _m5, sh = AutoForensicEngine.capture_forensic_screenshot(scr_dir)
        if path:
            self.viewer.append(f"[📸] Forensic Screenshot Captured: {path}\n     SHA-256: {sh}")
            self.load_dir_with_tamper_check(scr_dir)

    def run_global_search(self):
        kw = self.txt_search.text().strip()
        if kw:
            self.search_results.setText(AutoForensicEngine.search_keyword_in_case(self.active_case_dir, kw))

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
            QMessageBox.warning(self, "Target Offline", "Enable USB Debugging and tap 'Allow' on the phone.")
            return
        intake_data = {
            "case_id": self.txt_case.text().strip() or f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "evidence_tag": self.txt_tag.text().strip() or "EVID-001",
            "examiner": self.txt_examiner.text().strip() or "Kaleem Ullah",
            "location": self.txt_location.text().strip() or "DIRCYBER Lab",
            "condition": self.txt_condition.text().strip() or "Powered On",
        }
        cdir = os.path.join(self.output_base, f"{intake_data['case_id']}_{datetime.now().strftime('%H%M%S')}")
        os.makedirs(cdir, exist_ok=True)
        self.active_case_dir = cdir

        opts = {
            "calls": self.chk_calls.isChecked(),
            "sms": self.chk_sms.isChecked(),
            "audit": self.chk_audit.isChecked(),
            "storage": self.chk_storage.isChecked(),
            "whatsapp": self.chk_whatsapp.isChecked(),
        }
        self.btn_start.setEnabled(False)
        self.viewer.clear()
        self.worker = CompleteWorkflowWorker(cdir, intake_data, opts)
        self.worker.log_signal.connect(lambda m: self.viewer.append(m))
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.audit_signal.connect(self.audit_view.setText)
        self.worker.timeline_signal.connect(self.timeline_view.setText)
        self.worker.finished_signal.connect(self.on_done)
        self.worker.start()

    def on_done(self, cdir, rpath, _pdf):
        self.btn_start.setEnabled(True)
        self.load_dir_with_tamper_check(cdir)
        if rpath and os.path.exists(rpath):
            webbrowser.open(f"file://{rpath}")

    def on_tree_clicked(self, idx):
        p = self.fs_model.filePath(idx)
        if os.path.isdir(p):
            self.active_case_dir = p
            self.load_dir_with_tamper_check(p)
        elif os.path.isfile(p):
            self.viewer.setText(AutoForensicEngine.format_preview(p))

    def on_file_selected(self, row, _col):
        fn = self.table.item(row, 0).text()
        fp = os.path.join(self.current_dir, fn)
        if os.path.isfile(fp):
            self.viewer.setText(AutoForensicEngine.format_preview(fp))

def global_exception_handler(exctype, value, tb):
    print("".join(traceback.format_exception(exctype, value, tb)))

if __name__ == "__main__":
    sys.excepthook = global_exception_handler
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    win = DirCyberTacticalGUI()
    win.show()
    sys.exit(app.exec())
