# WDP: Web Data Protocol

WDP is a simplified, lightweight alternative to HTTP, designed for speed and ease of use. It comes with its own markup language, **EasyWDL**, specifically designed to be accessible for beginners and children.

## Key Features
- **Dual Protocol Support**: 
  - **WDP/1.0**: Lightweight protocol on port 7070.
  - **WDPS**: Secure version with SSL/TLS encryption on port 7071.
- **EasyWDL**: A markup language with symmetric tags: `(tag) content (tag)`.
- **Secure Browser**: Built-in support for `wdps://` URLs with end-to-end encryption.
- **Portable**: Script included to package the browser into a standalone executable.
- **Native Android App**: Functional WDP/WDPS browser for mobile devices.
- **VPS Ready**: Deployable to any Linux environment.

## Quick Start

### 1. Requirements
Ensure you have the necessary system dependencies (especially on Debian/Ubuntu):
```bash
sudo apt update && sudo apt install -y python3-tk python3-pil.imagetk python3-requests python3-venv
```

### 2. Run the Browser
```bash
python3 wdp_browser.py
```

### 3. Build Executable (Linux)
```bash
./build_app.sh
```

### 4. Build Android App
```bash
cd android
gradle assembleDebug
```

## EasyWDL Syntax Example
```wdl
(title) My Website (title)
(center) (image) https://picsum.photos/600/400 (image) (center)
(text) Hello, this is WDP! (text)
(link:wdp://home) Go Home (link:wdp://home)
```

## The Registry (Fake DNS)
> [!WARNING]
> The `wdp_registry.json` file is a **local shortcut registry**. 
> - It allows you to use friendly names like `wdp://home` instead of `localhost`.
> - If a name is **not** in this file, the browser will attempt to resolve it using the real internet DNS.
> - Avoid sharing your private registry file if it contains sensitive internal IPs.

## Project Structure
- `wdp_server.py`: The WDP server implementation (supports WDP/1.0 and WDPS).
- `wdp_browser.py`: The GUI browser with EasyWDL support.
- `wdp_registry.json`: Local name resolution shortcuts.
- `www/`: Directory for your WDL and HTML files.
- `build_app.sh`: Automated build script for Linux/Debian.
- `generate_certs.sh`: Script to generate SSL/TLS certificates for WDPS.
