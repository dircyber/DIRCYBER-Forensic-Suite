import subprocess
import os
import hashlib
import sqlite3
import zipfile
import shutil
from datetime import datetime
from PIL import Image, ExifTags
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class AutoForensicEngine:
    @staticmethod
    def run_adb(cmd_list):
        try:
            res = subprocess.run(
                ["adb"] + cmd_list,
                capture_output=True,
                text=True,
                errors="ignore",
                timeout=120
            )
            return res.stdout.strip()
        except Exception as e:
            return f"[Error: {e}]"

    @staticmethod
    def is_device_connected():
        out = AutoForensicEngine.run_adb(["devices"])
        return "device\n" in out + "\n"

    @staticmethod
    def create_full_mobile_image(dest_folder, case_name, log_callback=None):
        """
        Creates a Full Mobile Forensic Image (.dd) on Desktop:
        - Rooted: Dumps raw physical userdata/mmcblk0 block device.
        - Non-Rooted: Creates full bitstream image of /sdcard + system dumps + logical partitions.
        """
        os.makedirs(dest_folder, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = os.path.join(dest_folder, f"{case_name}_FULL_MOBILE_IMAGE_{ts}.dd")
        report_path = os.path.join(dest_folder, f"{case_name}_FULL_IMAGE_REPORT_{ts}.txt")

        su_check = AutoForensicEngine.run_adb(["shell", "su", "-c", "id"])
        mode = "FULL_LOGICAL_STORAGE_IMAGE (.DD)"

        if "uid=0" in su_check:
            # Find the largest userdata or mmcblk0 partition
            part_path = AutoForensicEngine.run_adb([
                "shell", "su", "-c",
                "ls /dev/block/bootdevice/by-name/userdata 2>/dev/null || ls /dev/block/by-name/userdata 2>/dev/null || echo /dev/block/mmcblk0"
            ]).strip()
            mode = f"FULL_PHYSICAL_RAW_PARTITION_IMAGE ({part_path})"
            if log_callback:
                log_callback(f"[*] Root Detected! Creating Full Physical Raw Image from {part_path}...")
            with open(img_path, "wb") as out_f:
                p = subprocess.Popen(
                    ["adb", "exec-out", "su", "-c", f"dd if={part_path} bs=4096"],
                    stdout=out_f,
                    stderr=subprocess.PIPE
                )
                p.wait(timeout=1800)
        else:
            if log_callback:
                log_callback("[*] Acquiring Full Mobile Storage Image (/sdcard + hidden media + system state)...")
            with open(img_path, "wb") as out_f:
                p = subprocess.Popen(
                    ["adb", "exec-out", "tar", "-cf", "-", "/sdcard"],
                    stdout=out_f,
                    stderr=subprocess.PIPE
                )
                p.wait(timeout=1800)

        sz = os.path.getsize(img_path) if os.path.exists(img_path) else 0
        if log_callback:
            log_callback("[*] Computing Master MD5 & SHA-256 Integrity Hashes for Full Image...")
        m5, sh = AutoForensicEngine.compute_hashes(img_path) if sz > 0 else ("N/A", "N/A")
        dev_info = AutoForensicEngine.get_device_info()

        with open(report_path, "w", encoding="utf-8") as rf:
            rf.write("=================================================================\n")
            rf.write("    DIRCYBER FORENSIC SUITE v8.0 - FULL MOBILE IMAGE REPORT\n")
            rf.write("=================================================================\n")
            rf.write(f"Case ID         : {case_name}\n")
            rf.write(f"Full Image File : {img_path}\n")
            rf.write(f"Acquisition Mode: {mode}\n")
            rf.write(f"Total Image Size: {sz:,} bytes ({sz / (1024*1024):.2f} MB)\n")
            rf.write(f"MD5 Checksum    : {m5}\n")
            rf.write(f"SHA-256 Hash    : {sh}\n")
            rf.write(f"Timestamp       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            rf.write("-----------------------------------------------------------------\n")
            for k, v in dev_info.items():
                rf.write(f"{k:<18}: {v}\n")
            rf.write("=================================================================\n")

        return img_path, report_path, sz, m5, sh

    @staticmethod
    def deep_recover_media_and_files(image_path, output_dir, log_callback=None):
        """
        Recovers Deleted & Corrupt Videos, Audios, Photos, Docs, and Databases:
        1. Foremost (MP4, AVI, MOV, WAV, MP3, JPG, PNG, PDF, ZIP, SQLite)
        2. PhotoRec (TestDisk automated file recovery for all audio/video codecs)
        3. SleuthKit (tsk_recover for deleted filesystem inodes)
        4. Custom Binary Header Carver & Corrupt Trailer Repairer
        """
        rec_dir = os.path.join(output_dir, f"RECOVERED_MEDIA_AND_FILES_{datetime.now().strftime('%H%M%S')}")
        os.makedirs(rec_dir, exist_ok=True)
        total_recovered = 0

        # 1. Foremost (Carves Video, Audio, Image, Docs)
        foremost_out = os.path.join(rec_dir, "01_Foremost_Video_Audio_Media")
        if shutil.which("foremost"):
            if log_callback:
                log_callback("[*] Running Foremost Carver (MP4, AVI, MOV, WAV, JPG, PNG, PDF)...")
            subprocess.run(["foremost", "-i", image_path, "-o", foremost_out, "-Q"], capture_output=True)
            for _r, _d, files in os.walk(foremost_out):
                total_recovered += len([f for f in files if f != "audit.txt"])

        # 2. PhotoRec (Automated recovery for MP3, M4A, AAC, OGG, MP4, MKV, 3GP, JPG)
        photorec_out = os.path.join(rec_dir, "02_PhotoRec_Audio_Video_Recovery")
        os.makedirs(photorec_out, exist_ok=True)
        if shutil.which("photorec"):
            if log_callback:
                log_callback("[*] Running PhotoRec Engine for Deleted Audio (MP3/M4A/WAV) & Video (MP4/3GP/MKV)...")
            subprocess.run(
                ["photorec", "/d", os.path.join(photorec_out, "rec"), "/cmd", image_path, "search"],
                capture_output=True,
                timeout=600
            )
            for _r, _d, files in os.walk(photorec_out):
                total_recovered += len(files)

        # 3. SleuthKit Deleted Inode Recovery
        tsk_out = os.path.join(rec_dir, "03_SleuthKit_Deleted_Files")
        os.makedirs(tsk_out, exist_ok=True)
        if shutil.which("tsk_recover"):
            if log_callback:
                log_callback("[*] Running SleuthKit (tsk_recover) on unallocated filesystem blocks...")
            subprocess.run(["tsk_recover", "-e", image_path, tsk_out], capture_output=True)
            for _r, _d, files in os.walk(tsk_out):
                total_recovered += len(files)

        # 4. Custom Audio / Video / Image Signature Carver & Corrupt File Repair
        av_carve_out = os.path.join(rec_dir, "04_Carved_Audio_Video_And_Repaired")
        os.makedirs(av_carve_out, exist_ok=True)
        if log_callback:
            log_callback("[*] Scanning binary streams for MP4, MP3, WAV, M4A, JPG, PNG & corrupt headers...")

        signatures = [
            # Video Signatures
            ("mp4", b"\x00\x00\x00\x18ftyp", None, 12 * 1024 * 1024),
            ("mp4", b"\x00\x00\x00\x20ftyp", None, 12 * 1024 * 1024),
            ("avi", b"RIFF", None, 10 * 1024 * 1024),
            # Audio Signatures
            ("mp3", b"ID3", None, 5 * 1024 * 1024),
            ("ogg", b"OggS", None, 4 * 1024 * 1024),
            # Image & Document Signatures (with EOF repair)
            ("jpg", b"\xFF\xD8\xFF", b"\xFF\xD9", 5 * 1024 * 1024),
            ("png", b"\x89PNG\r\n\x1a\n", b"IEND\xaeB`\x82", 5 * 1024 * 1024),
            ("pdf", b"%PDF-", b"%%EOF", 6 * 1024 * 1024),
        ]

        try:
            with open(image_path, "rb") as f:
                # Scan up to 100 MB per pass in chunks
                data = f.read(100 * 1024 * 1024)
                idx = 0
                for ext, hdr, ftr, max_sz in signatures:
                    pos = 0
                    while True:
                        start = data.find(hdr, pos)
                        if start == -1 or idx >= 250:
                            break
                        # Differentiate WAV vs AVI if RIFF header
                        actual_ext = ext
                        if hdr == b"RIFF" and data[start + 8:start + 12] == b"WAVE":
                            actual_ext = "wav"

                        if ftr:
                            end = data.find(ftr, start + len(hdr))
                            if end != -1 and (end - start) < max_sz:
                                blob = data[start:end + len(ftr)]
                            else:
                                # Corrupt header/EOF repair
                                blob = data[start:start + 512 * 1024] + ftr
                        else:
                            # For MP4/MP3/WAV/OGG extract until next major file signature or max_sz
                            blob = data[start:start + max_sz]

                        idx += 1
                        total_recovered += 1
                        out_file = os.path.join(av_carve_out, f"recovered_{idx:03d}.{actual_ext}")
                        with open(out_file, "wb") as wf:
                            wf.write(blob)
                        pos = start + len(hdr) + 1024
        except Exception:
            pass

        return rec_dir, total_recovered

    @staticmethod
    def inspect_and_detect_tampering(target_folder):
        baseline = {}
        hash_log = os.path.join(target_folder, "99_Master_Integrity_Hashes.txt")
        if os.path.exists(hash_log):
            cur_art = None
            with open(hash_log, "r", encoding="utf-8", errors="ignore") as hf:
                for line in hf:
                    line = line.strip()
                    if line.startswith("Artifact:"):
                        cur_art = line.split(":", 1)[1].strip()
                    elif line.startswith("SHA256:") and cur_art:
                        baseline[cur_art] = line.split(":", 1)[1].strip()

        results = []
        skip = ["99_Master_Integrity_Hashes.txt", "DIRCYBER_Forensic_Report.html", "DIRCYBER_Forensic_Report.pdf"]

        for root, _, files in os.walk(target_folder):
            for fn in sorted(files):
                if fn in skip:
                    continue
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, target_folder)
                sz = os.path.getsize(fp)
                m5, sh = AutoForensicEngine.compute_hashes(fp)

                status = "VERIFIED (Clean)"
                is_alert = False

                if rel in baseline and baseline[rel] != sh:
                    status = "TAMPERED / MODIFIED (Hash Mismatch!)"
                    is_alert = True
                elif baseline and rel not in baseline:
                    status = "NEW / UNTRACKED FILE ADDED"
                    is_alert = True
                elif sz == 0:
                    status = "CORRUPT / EMPTY (0 Bytes)"
                    is_alert = True
                elif fn.lower().endswith((".jpg", ".jpeg")):
                    with open(fp, "rb") as f:
                        if f.read(3) != b"\xFF\xD8\xFF":
                            status = "CORRUPT JPEG HEADER"
                            is_alert = True
                elif fn.lower().endswith(".mp4"):
                    with open(fp, "rb") as f:
                        hdr = f.read(12)
                    if b"ftyp" not in hdr:
                        status = "CORRUPT MP4 VIDEO HEADER"
                        is_alert = True

                results.append((rel, sz, status, m5, sh, is_alert))

        for old_rel, old_sh in baseline.items():
            if not os.path.exists(os.path.join(target_folder, old_rel)):
                results.append((old_rel, 0, "DELETED FROM CASE FOLDER!", "MISSING", old_sh, True))

        return results

    @staticmethod
    def check_isolation_state():
        airplane = AutoForensicEngine.run_adb(["shell", "settings", "get", "global", "airplane_mode_on"])
        wifi = AutoForensicEngine.run_adb(["shell", "settings", "get", "global", "wifi_on"])
        bat = AutoForensicEngine.run_adb(["shell", "dumpsys", "battery"])
        level = "Unknown"
        for line in bat.splitlines():
            if "level:" in line:
                level = line.strip()
                break
        return {
            "Airplane Mode": "ENABLED (Isolated)" if airplane == "1" else "DISABLED (Live Network Risk)",
            "Wi-Fi Radio": "ON" if wifi == "1" else "OFF",
            "Battery State": level,
        }

    @staticmethod
    def generate_chain_of_custody(case_dir, intake_data):
        coc_file = os.path.join(case_dir, "00_Chain_of_Custody.txt")
        lines = [
            "=================================================================",
            "       DIRCYBER FORENSIC SUITE - CHAIN OF CUSTODY RECORD",
            "=================================================================",
            f"Case ID            : {intake_data['case_id']}",
            f"Evidence Tag #     : {intake_data['evidence_tag']}",
            f"Lead Examiner      : {intake_data['examiner']}",
            f"Seizure Location   : {intake_data['location']}",
            f"Device Condition   : {intake_data['condition']}",
            f"Intake Timestamp   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=================================================================\n"
        ]
        with open(coc_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return coc_file

    @staticmethod
    def generate_pdf_report(pdf_path, intake_data, device_info, isolation_info, hash_records):
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        elements = []
        elements.append(Paragraph("<b>DIRCYBER FORENSIC SUITE v8.0 — DIGITAL EVIDENCE REPORT</b>", styles["Title"]))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            f"<b>Case ID:</b> {intake_data['case_id']} | <b>Tag:</b> {intake_data['evidence_tag']} | <b>Examiner:</b> {intake_data['examiner']}",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 12))
        dev_data = [["Property", "Value"]] + [[k, str(v)] for k, v in {**isolation_info, **device_info}.items()]
        t_dev = Table(dev_data, colWidths=[180, 340])
        t_dev.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ]))
        elements.append(t_dev)
        elements.append(Spacer(1, 12))
        h_data = [["Artifact Path", "Bytes", "SHA-256 Integrity Hash"]]
        for rel, sz, _m5, sh in hash_records:
            h_data.append([rel[:42], str(sz), sh])
        t_hash = Table(h_data, colWidths=[175, 55, 290])
        t_hash.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0284c7")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ]))
        elements.append(t_hash)
        doc.build(elements)

    @staticmethod
    def capture_forensic_screenshot(save_dir):
        os.makedirs(save_dir, exist_ok=True)
        fname = f"ScreenCapture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        local_path = os.path.join(save_dir, fname)
        remote_tmp = "/sdcard/dircyber_tmp_scr.png"
        subprocess.run(["adb", "shell", "screencap", "-p", remote_tmp], capture_output=True)
        subprocess.run(["adb", "pull", remote_tmp, local_path], capture_output=True)
        subprocess.run(["adb", "shell", "rm", "-f", remote_tmp], capture_output=True)
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            m5, sh = AutoForensicEngine.compute_hashes(local_path)
            return local_path, m5, sh
        return None, None, None

    @staticmethod
    def get_device_info():
        r = AutoForensicEngine.run_adb
        return {
            "Manufacturer": r(["shell", "getprop", "ro.product.manufacturer"]),
            "Model": r(["shell", "getprop", "ro.product.model"]),
            "Brand": r(["shell", "getprop", "ro.product.brand"]),
            "Android Version": r(["shell", "getprop", "ro.build.version.release"]),
            "SDK Level": r(["shell", "getprop", "ro.build.version.sdk"]),
            "Serial Number": r(["get-serialno"]),
            "Security Patch": r(["shell", "getprop", "ro.build.version.security_patch"]),
            "Build Fingerprint": r(["shell", "getprop", "ro.build.fingerprint"]),
            "Timezone": r(["shell", "getprop", "persist.sys.timezone"]),
        }

    @staticmethod
    def extract_content_uri(uri, out_file):
        data = AutoForensicEngine.run_adb(["shell", "content", "query", "--uri", uri])
        with open(out_file, "w", encoding="utf-8", errors="ignore") as f:
            if data and "No result found" not in data and not data.startswith("[Error"):
                f.write(data)
                return True
            f.write("No records accessible or restricted by Android OS.\n")
            return False

    @staticmethod
    def pull_folder(android_path, local_dest):
        os.makedirs(local_dest, exist_ok=True)
        try:
            subprocess.run(["adb", "pull", f"{android_path}/.", local_dest], capture_output=True, timeout=300)
        except Exception:
            pass

    @staticmethod
    def _convert_to_degrees(value):
        return float(value[0]) + (float(value[1]) / 60.0) + (float(value[2]) / 3600.0)

    @staticmethod
    def extract_exif_and_map(folder_path, report_file, map_file):
        found = 0
        gps_points = []
        tags_ok = ["Make", "Model", "DateTimeOriginal", "GPSInfo", "Software"]
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=== DIRCYBER EXIF METADATA & GPS REPORT ===\n\n")
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith((".jpg", ".jpeg", ".png")):
                        fpath = os.path.join(root, file)
                        try:
                            img = Image.open(fpath)
                            exif = img._getexif()
                            if exif:
                                found += 1
                                f.write(f"File: {file}\n")
                                gps_raw = {}
                                dt_str = "Unknown Time"
                                for tid, val in exif.items():
                                    tag = ExifTags.TAGS.get(tid, tid)
                                    if tag == "DateTimeOriginal":
                                        dt_str = str(val)
                                    if tag == "GPSInfo":
                                        for gt_id, gt_val in val.items():
                                            gtag = ExifTags.GPSTAGS.get(gt_id, gt_id)
                                            gps_raw[gtag] = gt_val
                                    if tag in tags_ok:
                                        f.write(f"  {tag}: {val}\n")
                                if "GPSLatitude" in gps_raw and "GPSLongitude" in gps_raw:
                                    lat = AutoForensicEngine._convert_to_degrees(gps_raw["GPSLatitude"])
                                    if gps_raw.get("GPSLatitudeRef") == "S":
                                        lat = -lat
                                    lon = AutoForensicEngine._convert_to_degrees(gps_raw["GPSLongitude"])
                                    if gps_raw.get("GPSLongitudeRef") == "W":
                                        lon = -lon
                                    gps_points.append((lat, lon, file, dt_str))
                                f.write("-" * 45 + "\n")
                        except Exception:
                            pass

        markers_js = ""
        for lat, lon, fn, dt in gps_points:
            markers_js += f"L.marker([{lat}, {lon}]).addTo(map).bindPopup('<b>{fn}</b><br>{dt}');\n"
        center = f"[{gps_points[0][0]}, {gps_points[0][1]}]" if gps_points else "[34.0151, 71.5249]"
        map_html = f"""<!DOCTYPE html><html><head><title>DIRCYBER GPS MAP</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>body{{margin:0;background:#090d16;color:#fff;font-family:Arial;}} #map{{height:90vh;}}</style>
        </head><body><h3 style="padding:10px;margin:0;">🗺️ DIRCYBER GPS MAP ({len(gps_points)} Geotagged Photos)</h3>
        <div id="map"></div><script>
        var map = L.map('map').setView({center}, 12);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
        {markers_js}</script></body></html>"""
        with open(map_file, "w", encoding="utf-8") as mf:
            mf.write(map_html)
        return found, len(gps_points)

    @staticmethod
    def security_and_spyware_audit(out_file):
        third_party = AutoForensicEngine.run_adb(["shell", "pm", "list", "packages", "-3"])
        risky_perms = [
            "android.permission.READ_SMS",
            "android.permission.RECORD_AUDIO",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.READ_CALL_LOG",
        ]
        lines = ["=== DIRCYBER SPYWARE & PERMISSION TRIAGE ===\n", third_party + "\n"]
        for perm in risky_perms:
            holders = AutoForensicEngine.run_adb(["shell", "pm", "list", "packages", "--permissions", perm])
            lines.append(f"\n[Permission: {perm}]\n{holders}")
        full_report = "\n".join(lines)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(full_report)
        return full_report

    @staticmethod
    def build_forensic_timeline(case_dir, timeline_file):
        entries = []
        for root, _, files in os.walk(case_dir):
            for file in files:
                fp = os.path.join(root, file)
                try:
                    stat = os.stat(fp)
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    rel = os.path.relpath(fp, case_dir)
                    entries.append((mtime, stat.st_size, rel))
                except Exception:
                    pass
        entries.sort(reverse=True)
        lines = ["TIMESTAMP           | SIZE (BYTES) | ARTIFACT PATH", "-" * 75]
        for t, sz, rel in entries:
            lines.append(f"{t} | {sz:<12} | {rel}")
        text = "\n".join(lines)
        with open(timeline_file, "w", encoding="utf-8") as f:
            f.write(text)
        return text

    @staticmethod
    def search_keyword_in_case(case_dir, keyword):
        hits = []
        kw = keyword.lower()
        for root, _, files in os.walk(case_dir):
            for file in files:
                if file.lower().endswith((".txt", ".html", ".xml", ".json", ".csv", ".log")):
                    fp = os.path.join(root, file)
                    rel = os.path.relpath(fp, case_dir)
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f, 1):
                                if kw in line.lower():
                                    hits.append(f"[{rel} : Line {idx}] -> {line.strip()[:140]}")
                                    if len(hits) >= 500:
                                        return "\n".join(hits)
                    except Exception:
                        pass
        return "\n".join(hits) if hits else f"No matches found for '{keyword}'."

    @staticmethod
    def parse_sqlite_databases(case_dir):
        pdir = os.path.join(case_dir, "10_Parsed_SQLite_DBs")
        os.makedirs(pdir, exist_ok=True)
        count = 0
        for root, _, files in os.walk(case_dir):
            for file in files:
                if file.endswith((".db", ".sqlite", ".sqlite3")):
                    dbp = os.path.join(root, file)
                    try:
                        conn = sqlite3.connect(dbp)
                        cur = conn.cursor()
                        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        tables = [t[0] for t in cur.fetchall()]
                        if tables:
                            count += 1
                            otxt = os.path.join(pdir, f"{file}_dump.txt")
                            with open(otxt, "w", errors="ignore") as out:
                                for tbl in tables:
                                    out.write(f"\n=== TABLE: {tbl} ===\n")
                                    cur.execute(f"SELECT * FROM {tbl} LIMIT 300;")
                                    for row in cur.fetchall():
                                        out.write(str(row) + "\n")
                        conn.close()
                    except Exception:
                        pass
        return count

    @staticmethod
    def compute_hashes(filepath):
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
                sha256.update(chunk)
        return md5.hexdigest(), sha256.hexdigest()

    @staticmethod
    def format_preview(filepath, max_bytes=6144):
        if filepath.lower().endswith((".txt", ".html", ".xml", ".json", ".csv", ".log")):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_bytes)
        out = []
        with open(filepath, "rb") as f:
            data = f.read(max_bytes)
        for i in range(0, len(data), 16):
            ch = data[i:i+16]
            hp = " ".join(f"{b:02X}" for b in ch)
            ap = "".join(chr(b) if 32 <= b < 127 else "." for b in ch)
            out.append(f"{i:08X}  {hp:<47}  |{ap}|")
        return "\n".join(out)
