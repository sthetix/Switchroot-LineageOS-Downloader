# Switchroot LineageOS Downloader (Windows EXE)

<p align="center" width="100%">
    <img width="450px" src="https://github.com/sthetix/SLD/blob/main/screen.png" alt="Screenshot">
</p>

*Example screenshot of the application in action.*

**Switchroot LineageOS Downloader** is a lightweight Windows application designed to simplify the process of downloading and organizing LineageOS builds for the Nintendo Switch (Switchroot). Whether you're setting up LineageOS for the tablet or TV variant, this tool automates the download process, verifies file integrity using SHA-256 checksums, and organizes files into the correct folder structure for easy installation.

---

## Features

- **Easy-to-Use GUI**: A clean and intuitive interface for seamless navigation.
- **Dark Theme**: A modern dark theme for comfortable usage.
- **Automatic Folder Structure**: Creates the necessary folders (`switchroot`, `bootloader`, etc.) and generates the required `android.ini` file.
- **Multi-Threaded Downloads**: Downloads multiple files simultaneously for faster performance.
- **Checksum Verification**: Ensures file integrity by verifying SHA-256 checksums for downloaded files.
- **Resumable Downloads**: Supports resuming interrupted downloads, saving time and bandwidth.
- **Progress Tracking**: Real-time progress updates with a progress bar and detailed download statistics.
- **Error Handling**: Retries failed downloads automatically and logs errors for troubleshooting.
- **Customizable Download Directory**: Users can select a custom download folder.
- **Portable**: No installation required; just download the EXE and run it.

---

## Download

You can download the latest version of the application from the [Releases](https://github.com/your-username/switchroot-lineageos-downloader/releases) section.

---

## Usage

1. **Download the EXE**: Download the `LineageOS_Downloader.exe` file from the Releases section.
2. **Run the Application**: Double-click the EXE file to launch the application.
3. **Select Variant**: Choose between the **Tablet** or **TV** variant of LineageOS.
4. **Check Latest Build**: Click the "Check Build" button to fetch the latest build information.
5. **Select Download Folder**: Choose a directory where the files will be downloaded and organized.
6. **Start Download**: Click the "Download" button to begin downloading.
7. **Monitor Progress**: Track the download progress in real time using the progress bar and logs.
8. **Verify Files**: The application automatically verifies the integrity of downloaded files using SHA-256 checksums.

---

## Folder Structure

After downloading, the files are organized into the following structure:

# LineageOS Repository Structure
```

LineageOS-{version}-{date}-{variant}/
├── switchroot/
│ ├── install/
│ │ ├── boot.img
│ │ ├── recovery.img
│ │ └── nx-plat.dtimg
│ └── android/
│ ├── bl31.bin
│ ├── bl33.bin
│ ├── boot.scr
│ ├── icon_android_hue.bmp
│ └── bootlogo_android.bmp
├── bootloader/
│ └── ini/
│ └── android.ini
└── lineage-{version}-{date}-nightly-nx_tab-signed.zip
```


---

## Logs

All actions and errors are logged in `lineageos_downloader.log` (created in the same directory as the EXE) for easy troubleshooting.

---

## Frequently Asked Questions (FAQ)

### 1. **Is this application safe to use?**
   - Yes, the application is safe to use. It does not contain any malware or harmful code. The source code is available for review (if provided).

### 2. **Can I use this on macOS or Linux?**
   - This EXE is designed for Windows only. You can run the Python script directly if the source code is available for macOS or Linux.

### 3. **What if the download fails?**
   - The application automatically retries failed downloads up to 3 times. If the issue continues, please check the logs for more details.

### 4. **Can I change the download folder?**
   - You can select a custom download folder using the "Select Folder" button.

### 5. **How do I verify the checksum of downloaded files?**
   - The application automatically verifies the SHA-256 checksum of each file. If the checksum does not match, the file will be re-downloaded.

---

## Support

If you encounter any issues or have suggestions for improvement, please open an [issue](https://github.com/sthetix/SLD/issues) on GitHub.


---

## License

This project is licensed under the **MIT License**. Please take a look at the [LICENSE](LICENSE) file for details.

---

## Why Use This Tool?

- **Saves Time**: Automates the download and organization process, so you don’t have to create folders or verify files manually.
- **User-Friendly**: Designed with a simple and intuitive interface for beginners and advanced users.
- **Reliable**: Ensures file integrity with checksum verification and retries failed downloads automatically.

---

## Credits

- Built with Python and `tkinter`.
- Special thanks to the **Switchroot team** for their work on LineageOS for the Nintendo Switch.

---

Enjoy using the **Switchroot LineageOS Downloader**! If you find this tool helpful, consider giving it a ⭐ on GitHub.
