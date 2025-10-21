import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import zipfile
import sys
import ctypes
import hashlib

class LineageOSDownloader:
    def __init__(self, master):
        self.master = master
        self.master.title("Switchroot LineageOS Downloader")
        self.master.geometry("500x450")
        self.style = ttk.Style()

        # Define the app version
        self.app_version = "v1.0.2"  # Updated version

        # Configure dark theme
        self.style.theme_use('clam')
        self.style.configure('.', background='#2b2b2b', foreground='white', font=('Segoe UI', 10))
        self.style.configure('TButton', background='#3d3d3d', bordercolor='#4d4d4d', relief='flat')
        self.style.map('TButton', 
                       background=[('active', '#4d4d4d'), ('disabled', '#2b2b2b')],
                       foreground=[('active', 'white')])
        self.style.configure('TRadiobutton', background='#2b2b2b', foreground='white')
        self.style.map('TRadiobutton',
                       background=[('active', '#4d4d4d'), ('selected', '#4d4d4d')],
                       foreground=[('active', 'white'), ('selected', 'white')])
        self.style.configure('TCheckbutton', background='#2b2b2b', foreground='white')
        self.style.map('TCheckbutton',
                       background=[('active', '#4d4d4d'), ('selected', '#4d4d4d')],
                       foreground=[('active', 'white'), ('selected', 'white')])
        self.style.configure("Horizontal.TProgressbar", 
                             troughcolor='#3d3d3d', 
                             background='#00cc66',
                             thickness=15)

        # Initialize variables
        self.device_type = tk.StringVar(value="tablet")
        self.download_gapps = tk.BooleanVar(value=False)  # New variable for GApps
        self.download_urls = []
        self.total_downloaded = 0
        self.total_size = 0
        self.download_dir = os.path.expanduser("~/Downloads")
        self.cancel_download = False
        self.retry_attempts = 3
        self.permanent_links = [
            "https://wiki.lineageos.org/images/device_specific/nx/bootlogo_android.bmp",
            "https://wiki.lineageos.org/images/device_specific/nx/icon_android_hue.bmp"
        ]
        self.last_update_time = 0
        self.latest_build = None
        self.target_dir = None
        self.failed_downloads = []
        self.gapps_url = None  # Store GApps URL
        self.gapps_filename = None  # Store GApps filename
        self.gapps_checksums = {}  # Store checksums for verification

        # Configure logging
        logging.basicConfig(
            filename='lineageos_downloader.log',
            level=logging.DEBUG,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )

        self.create_widgets()
        self.master.report_callback_exception = self.handle_gui_errors

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header_frame, text="⚡ Switchroot LineageOS Downloader", 
                  font=('Segoe UI', 14, 'bold')).pack()

        # Variants Selection
        variants_frame = ttk.LabelFrame(main_frame, text=" Choose Variants ", padding=10)
        variants_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(variants_frame, text="Tablet", variable=self.device_type, 
                        value="tablet").pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(variants_frame, text="TV", variable=self.device_type, 
                        value="tv").pack(side=tk.LEFT, padx=15)
        ttk.Checkbutton(variants_frame, text="Download MindTheGapps", 
                        variable=self.download_gapps).pack(side=tk.LEFT, padx=15)

        # Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        button_width = 15
        ttk.Button(btn_frame, text="🔄 Check Build", width=button_width,
                   command=self.check_latest_build).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📂 Select Folder", width=button_width,
                   command=self.select_download_dir).pack(side=tk.LEFT, padx=2)
        self.download_btn = ttk.Button(btn_frame, text="⏬ Download", width=button_width,
                                       command=self.start_download, state=tk.DISABLED)
        self.download_btn.pack(side=tk.LEFT, padx=2)
        self.cancel_btn = ttk.Button(btn_frame, text="⏹ Cancel", width=button_width,
                                     state=tk.DISABLED, command=self.cancel_download_process)
        self.cancel_btn.pack(side=tk.LEFT, padx=2)
        self.retry_btn = ttk.Button(btn_frame, text="🔄 Retry Failed", width=button_width,
                                    state=tk.DISABLED, command=self.retry_failed_downloads)
        self.retry_btn.pack(side=tk.LEFT, padx=2)

        # Build Info
        build_frame = ttk.Frame(main_frame)
        build_frame.pack(fill=tk.X, pady=5)
        ttk.Label(build_frame, text="Latest Build:", font=('Segoe UI', 10)).pack(side=tk.LEFT)
        self.build_label = ttk.Label(build_frame, text="-", font=('Segoe UI', 10, 'bold'),
                                     foreground='#00cc66')
        self.build_label.pack(side=tk.LEFT, padx=5)

        # Progress Bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        # Progress Text
        self.progress_label = ttk.Label(progress_frame, text="Ready", 
                                        font=('Segoe UI', 9), foreground='#888888')
        self.progress_label.pack(fill=tk.X)

        # Logs
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = tk.Text(log_frame, height=6, bg='#3d3d3d', fg='white',
                                insertbackground='white', wrap=tk.WORD, font=('Segoe UI', 9))
        vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=vsb.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Clear Logs Button and Version Label
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=5)
        clear_logs_button = ttk.Button(bottom_frame, text="🧹 Clear Logs", command=self.clear_logs, width=15)
        clear_logs_button.pack(side=tk.LEFT, expand=True, padx=(100, 10))
        self.version_label = ttk.Label(bottom_frame, text=f"Version: {self.app_version}", 
                                    font=('Segoe UI', 8), foreground='#888888')
        self.version_label.pack(side=tk.RIGHT, padx=10)

    def handle_gui_errors(self, exc_type, exc_value, traceback):
        logging.error("GUI Error", exc_info=(exc_type, exc_value, traceback))
        messagebox.showerror("Application Error", f"{exc_type.__name__}: {exc_value}")

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
        logging.info(message)

    def clear_logs(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.build_label.config(text="-")
        if self.download_dir and os.path.exists(self.download_dir):
            try:
                for filename in os.listdir(self.download_dir):
                    file_path = os.path.join(self.download_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                self.log_message(f"Cleared all files in the download directory: {self.download_dir}")
            except Exception as e:
                self.log_message(f"Error clearing download directory: {str(e)}")
        self.download_btn.config(state=tk.DISABLED)
        self.download_dir = None

    def select_download_dir(self):
        self.download_dir = filedialog.askdirectory()
        if self.download_dir:
            self.log_message(f"Download directory set to: {self.download_dir}")
            self.download_btn.config(state=tk.NORMAL)
            self.create_folders_and_ini()
        else:
            self.log_message("Using default download directory")

    def fetch_latest_build(self):
        device = "nx_tab" if self.device_type.get() == "tablet" else "nx"
        url = f"https://download.lineageos.org/api/v2/devices/{device}/builds"
        try:
            self.log_message(f"Fetching latest build from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            builds = response.json()
            if not builds:
                raise ValueError("No builds found in response")
            return max(builds, key=lambda x: x['date'])
        except Exception as e:
            self.log_message(f"Error fetching builds: {str(e)}")
            raise

    def fetch_gapps_url(self):
        if not self.latest_build:
            self.log_message("No build information available. Cannot fetch GApps.")
            return None, None
        version = self.latest_build['version']
        device_type = self.device_type.get().lower()
        gapps_suffix = "arm64" if device_type == "tablet" else "arm64-ATV"
        
        # Map LineageOS version to Android version
        version_map = {
            "20.0": "13",
            "21.0": "14",
            "22.0": "15",
            "22.1": "15"
        }
        android_version = version_map.get(version, "15")  # Default to 15 for unknown versions
        github_api = f"https://api.github.com/repos/MindTheGapps/{android_version}.0.0-{gapps_suffix}/releases/latest"
        
        try:
            self.log_message(f"Fetching MindTheGapps from: {github_api}")
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(github_api, headers=headers, timeout=10)
            response.raise_for_status()
            gapps_json = response.json()
            gapps_url = None
            gapps_filename = None
            for asset in gapps_json.get('assets', []):
                name = asset['name']
                if (f"MindTheGapps-{android_version}.0.0-{gapps_suffix}" in name and
                    "arm64" in name and name.endswith(".zip")):
                    gapps_url = asset['browser_download_url']
                    gapps_filename = name
                    break
            if not gapps_url:
                self.log_message("Error: No matching MindTheGapps package found!")
                return None, None
            self.log_message(f"Found MindTheGapps: {gapps_filename}")
            return gapps_url, gapps_filename
        except Exception as e:
            self.log_message(f"Error fetching MindTheGapps: {str(e)}")
            return None, None

    def check_latest_build(self):
        try:
            self.latest_build = self.fetch_latest_build()
            version = self.latest_build['version']
            date = self.latest_build['date'].replace("-", "")
            self.build_label.config(text=f"{version}-{date}")
            self.download_urls = [file['url'] for file in self.latest_build['files'] if 'super_empty.img' not in file['url']]
            # Store checksums for verification
            for file in self.latest_build['files']:
                if 'super_empty.img' not in file['url']:
                    self.gapps_checksums[file['url']] = file.get('sha256')
            # Fetch GApps URL if selected
            if self.download_gapps.get():
                self.gapps_url, self.gapps_filename = self.fetch_gapps_url()
                if self.gapps_url:
                    self.download_urls.append(self.gapps_url)
            self.log_message("Successfully fetched build information")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch build: {str(e)}")

    def create_folders_and_ini(self):
        if not self.latest_build:
            self.log_message("No build information available. Please check the latest build first.")
            return

        build_info = self.build_label.cget("text").split('-')
        version = build_info[0]
        date = build_info[1]
        device_type = "TV" if self.device_type.get().lower() == "tv" else "Tablet"
        folder_name = f"LineageOS-{version}-{date}-{device_type}"
        self.target_dir = os.path.join(self.download_dir, folder_name)

        try:
            os.makedirs(self.target_dir, exist_ok=True)
            os.makedirs(os.path.join(self.target_dir, "switchroot", "install"), exist_ok=True)
            os.makedirs(os.path.join(self.target_dir, "switchroot", "android"), exist_ok=True)
            os.makedirs(os.path.join(self.target_dir, "bootloader", "ini"), exist_ok=True)

            ini_content = """[LineageOS]
l4t=1
boot_prefixes=switchroot/android/
id=SWANDR
icon=switchroot/android/icon_android_hue.bmp
logopath=switchroot/android/bootlogo_android.bmp
r2p_action=self
; alarms_disable=1 uncomment to disable notifications for better battery life
; touch_skip_tuning=1 uncomment if your touchscreen is broken
; usb3_enable=1 uncomment for faster USB at expense of WiFi/BT quality
; ddr200_enable=1 uncomment for faster SD speed on models that support it (Samsung enabled by default)
; emmc=1 uncomment to boot from the internal eMMC (not reccomended, and requires a signifigantly different set of installation instructions/partitioning process)
"""
            with open(os.path.join(self.target_dir, "bootloader", "ini", "android.ini"), "w") as f:
                f.write(ini_content)

            self.log_message(f"Created folders and generated android.ini in: {self.target_dir}")
        except Exception as e:
            self.log_message(f"Error creating folders or generating ini file: {str(e)}")
            messagebox.showerror("Error", f"Failed to create folders or generate ini file: {str(e)}")

    def start_download(self):
        if not self.download_urls:
            messagebox.showwarning("Warning", "No files available to download")
            return
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.retry_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.prepare_and_start_download, daemon=True).start()

    def prepare_and_start_download(self):
        try:
            self.progress_bar['value'] = 0
            self.total_downloaded = 0
            self.cancel_download = False
            self.failed_downloads = []
            self.total_files = len(self.download_urls)
            self.log_message(f"Total files to download: {self.total_files}")
            self.progress_label.config(text="Starting download...")
            self.master.update_idletasks()

            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.download_file, url) 
                          for url in self.download_urls]
                for future in as_completed(futures):
                    if self.cancel_download:
                        break
            if not self.cancel_download:
                self.log_message("Download complete! Files are organized in the target folder.")
        except Exception as e:
            self.log_message(f"Download failed: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.master.after(0, self.reset_ui)

    def download_file(self, url):
        filename = os.path.basename(url)
        truncated_filename = (filename[:20] + '...') if len(filename) > 20 else filename

        # Determine the target folder based on file type
        if filename in ["boot.img", "recovery.img", "nx-plat.dtimg"]:
            target_folder = os.path.join(self.target_dir, "switchroot", "install")
        elif filename in ["bl31.bin", "bl33.bin", "boot.scr", "icon_android_hue.bmp", "bootlogo_android.bmp"]:
            target_folder = os.path.join(self.target_dir, "switchroot", "android")
        elif filename.startswith("MindTheGapps"):
            target_folder = self.target_dir  # GApps go to root folder
        else:
            target_folder = self.target_dir  # Default to root folder (e.g., LineageOS ZIP)

        os.makedirs(target_folder, exist_ok=True)
        file_path = os.path.join(target_folder, filename)
        temp_file_path = file_path + ".part"

        # Fetch the checksum from the API or None for GApps
        expected_checksum = self.gapps_checksums.get(url)

        for attempt in range(1, self.retry_attempts + 1):
            if self.cancel_download:
                return

            try:
                if os.path.exists(file_path):
                    if expected_checksum:
                        if self.verify_checksum(file_path, expected_checksum):
                            self.log_message(f"File already exists and is complete: {filename}")
                            return
                        else:
                            self.log_message(f"Existing file is corrupted. Deleting: {filename}")
                            os.remove(file_path)
                    else:
                        if filename.endswith(".zip") and not self.is_valid_zip(file_path):
                            self.log_message(f"Existing ZIP file is corrupted. Deleting: {filename}")
                            os.remove(file_path)
                        else:
                            self.log_message(f"File already exists: {filename}")
                            return

                self.log_message(f"Downloading {filename} (Attempt {attempt})")
                downloaded_size = 0
                if os.path.exists(temp_file_path):
                    downloaded_size = os.path.getsize(temp_file_path)
                    if expected_checksum:
                        partial_checksum = self.calculate_checksum(temp_file_path)
                        if not expected_checksum.startswith(partial_checksum):
                            self.log_message(f"Corrupted temp file detected: {filename}")
                            os.remove(temp_file_path)
                            downloaded_size = 0

                headers = {"Range": f"bytes={downloaded_size}-"} if downloaded_size else {}
                response = requests.get(url, headers=headers, stream=True, timeout=10)
                response.raise_for_status()

                total_size = int(response.headers.get('Content-Length', 0)) + downloaded_size
                with open(temp_file_path, 'ab' if downloaded_size else 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if self.cancel_download:
                            return
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            file_progress = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                            self.master.after(0, self.update_progress, truncated_filename, file_progress)

                if expected_checksum:
                    if not self.verify_checksum(temp_file_path, expected_checksum):
                        raise ValueError(f"Checksum mismatch for {filename}")
                elif filename.endswith(".zip"):
                    if not self.is_valid_zip(temp_file_path):
                        raise ValueError(f"Invalid ZIP file: {filename}")

                os.rename(temp_file_path, file_path)
                self.log_message(f"Finished download: {filename}")
                self.total_downloaded += 1
                return

            except Exception as e:
                self.log_message(f"Attempt {attempt} failed: {str(e)}")
                if attempt == self.retry_attempts:
                    self.failed_downloads.append(url)
                    self.log_message(f"Permanent failure for {filename}")

    def calculate_checksum(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def verify_checksum(self, file_path, expected_checksum):
        actual_checksum = self.calculate_checksum(file_path)
        return actual_checksum == expected_checksum

    def is_valid_zip(self, file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                return zip_ref.testzip() is None
        except zipfile.BadZipFile:
            return False

    def update_progress(self, filename, file_progress):
        try:
            current_time = time.time() * 1000
            if current_time - self.last_update_time < 100:
                return
            self.progress_bar["value"] = file_progress
            self.progress_label.config(
                text=f"Downloading {filename} ({file_progress:.1f}%) | Total {self.total_downloaded} of {self.total_files}",
                foreground='#00cc66'
            )
            self.last_update_time = current_time
        except ZeroDivisionError:
            self.progress_label.config(text="Calculating progress...")
        except Exception as e:
            logging.error(f"Progress update error: {e}")

    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def reset_ui(self):
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        if self.cancel_download:
            self.progress_label.config(text="Download Canceled", foreground='#ff4444')
        else:
            self.progress_label.config(text=f"Download Complete! {self.total_downloaded} of {self.total_files} files downloaded.", foreground='#00cc66')
        self.progress_bar["value"] = 0
        self.master.after(2000, lambda: self.progress_label.config(
            text="Ready", 
            foreground='#888888'
        ))
        if self.failed_downloads:
            self.retry_btn.config(state=tk.NORMAL)

    def cancel_download_process(self):
        self.cancel_download = True
        self.log_message("Canceling download...")
        self.progress_label.config(text="Canceling...", foreground='#ff4444')
        self.progress_bar['value'] = 0
        self.master.update_idletasks()

    def retry_failed_downloads(self):
        if not self.failed_downloads:
            self.log_message("No failed downloads to retry.")
            return
        self.log_message("Retrying failed downloads...")
        self.download_urls = self.failed_downloads
        self.failed_downloads = []
        self.start_download()

if __name__ == "__main__":
    root = tk.Tk()
    if getattr(sys, 'frozen', False):
        script_dir = sys._MEIPASS
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "icon.ico")
    try:
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Error setting icon: {e}")
    try:
        myappid = 'mycompany.lineageos.downloader'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"Error setting taskbar icon: {e}")
    app = LineageOSDownloader(root)
    root.mainloop()