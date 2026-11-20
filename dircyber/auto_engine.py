import subprocess
import os
import hashlib
import sqlite3
import zipfile
from datetime import datetime
from PIL import Image, ExifTags

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
    def capture_forensic_screenshot(save_dir):
        """Captures live device screenshot & computes SHA-256"""
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
            "Bootloader State": r(["shell", "getprop", "ro.boot.verifiedbootstate"]),
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
            subprocess.run(
                ["adb", "pull", f"{android_path}/.", local_dest],
                capture_output=True,
                timeout=300
            )
        except Exception:
            pass

    @staticmethod
    def _convert_to_degrees(value):
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    @staticmethod
    def extract_exif_and_map(folder_path, report_file, map_file):
        """Extracts EXIF metadata & builds an interactive Leaflet GPS map"""
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
        map_html = f"""<!DOCTYPE html><html><head><title>DIRCYBER GPS EVIDENCE MAP</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>body{{margin:0;background:#090d16;color:#fff;font-family:Arial;}} #map{{height:90vh;}}</style>
        </head><body><h3 style="padding:10px;margin:0;">🗺️ DIRCYBER GPS ARTIFACT MAP ({len(gps_points)} Geotagged Photos)</h3>
        <div id="map"></div><script>
        var map = L.map('map').setView({center}, 12);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
        {markers_js}</script></body></html>"""
        with open(map_file, "w", encoding="utf-8") as mf:
            mf.write(map_html)
        return found, len(gps_points)

    @staticmethod
    def carve_hidden_artifacts(case_dir):
        carve_dir = os.path.join(case_dir, "11_Carved_Hidden_Files")
        os.makedirs(carve_dir, exist_ok=True)
        signatures = {
            "jpg": (b"\xFF\xD8\xFF", b"\xFF\xD9"),
            "pdf": (b"%PDF-", b"%%EOF"),
        }
        carved_count = 0
        for root, _, files in os.walk(case_dir):
            if "11_Carved_Hidden_Files" in root:
                continue
            for file in files:
                fpath = os.path.join(root, file)
                try:
                    if os.path.getsize(fpath) > 15 * 1024 * 1024:
                        continue
                    with open(fpath, "rb") as f:
                        blob = f.read()
                    for ext, (header, footer) in signatures.items():
                        start = blob.find(header)
                        if start > 0:
                            end = blob.find(footer, start)
                            if end != -1:
                                carved_count += 1
                                out_name = f"carved_{carved_count}_{file}.{ext}"
                                with open(os.path.join(carve_dir, out_name), "wb") as cf:
                                    cf.write(blob[start:end + len(footer)])
                except Exception:
                    pass
        return carved_count

    @staticmethod
    def security_and_spyware_audit(out_file):
        third_party = AutoForensicEngine.run_adb(["shell", "pm", "list", "packages", "-3"])
        risky_perms = [
            "android.permission.READ_SMS",
            "android.permission.RECORD_AUDIO",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.READ_CALL_LOG",
            "android.permission.SYSTEM_ALERT_WINDOW",
        ]
        report_lines = [
            "=== DIRCYBER SPYWARE & PERMISSION TRIAGE ===\n",
            "--- Third-Party Sideloaded / User Installed Packages ---",
            third_party + "\n",
            "--- High-Risk Spyware Permission Holders ---"
        ]
        for perm in risky_perms:
            holders = AutoForensicEngine.run_adb(["shell", "pm", "list", "packages", "--permissions", perm])
            report_lines.append(f"\n[Permission: {perm}]\n{holders}")

        full_report = "\n".join(report_lines)
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
        """Global IOC / Keyword Search across all extracted text & parsed databases"""
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
    def create_sealed_evidence_zip(case_dir):
        """Packages entire case into a ZIP archive & computes master SHA-256 seal"""
        zip_path = f"{case_dir}_SEALED_EVIDENCE.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(case_dir):
                for file in files:
                    fp = os.path.join(root, file)
                    zf.write(fp, os.path.relpath(fp, case_dir))
        m5, sh = AutoForensicEngine.compute_hashes(zip_path)
        seal_txt = f"{zip_path}.SHA256.txt"
        with open(seal_txt, "w", encoding="utf-8") as sf:
            sf.write(f"DIRCYBER CHAIN-OF-CUSTODY EVIDENCE SEAL\nArchive: {os.path.basename(zip_path)}\n")
            sf.write(f"Timestamp: {datetime.now()}\nMD5   : {m5}\nSHA256: {sh}\n")
        return zip_path, sh

    @staticmethod
    def parse_sqlite_databases(case_dir):
        pdir = os.path.join(case_dir, "10_Parsed_SQLite_DBs")
        os.makedirs(pdir, exist_ok=True)
        count = 0
        exts = (".db", ".sqlite", ".sqlite3")
        for root, _, files in os.walk(case_dir):
            for file in files:
                if file.endswith(exts):
                    dbp = os.path.join(root, file)
                    try:
                        conn = sqlite3.connect(dbp)
                        cur = conn.cursor()
                        q = "SELECT name FROM sqlite_master WHERE type='table';"
                        cur.execute(q)
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
