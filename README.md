# WDP: Web Data Protocol

WDP is a simplified, lightweight alternative to HTTP, designed for speed and ease of use. It comes with its own markup language, **EasyWDL**, specifically designed to be accessible for beginners and children.

## Key Features
- **TCP-based Protocol**: Lightweight WDP/1.0 protocol on port 7070.
- **EasyWDL**: A markup language with symmetric tags: `(tag) content (tag)`.
- **Professional Browser**: Custom-built browser supporting images, centering, and name resolution.
- **Portable**: Built-in script to package the browser into a standalone executable.
- **VPS Ready**: Easily deployable to any Linux server.

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

### 3. Build Executable
```bash
./build_app.sh
```

## EasyWDL Syntax Example
```wdl
(title) My Website (title)
(center) (image) https://picsum.photos/600/400 (image) (center)
(text) Hello, this is WDP! (text)
(link:wdp://home) Go Home (link:wdp://home)
```

## Project Structure
- `wdp_server.py`: The WDP server implementation.
- `wdp_browser.py`: The GUI browser.
- `wdp_registry.json`: DNS simulation registry.
- `www/`: Directory for your WDL and HTML files.
- `build_app.sh`: Automated build script.
