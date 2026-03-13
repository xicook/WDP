import tkinter as tk
from tkinter import ttk, messagebox
import socket
import re
import json
import os
from PIL import Image, ImageTk
import io
import requests
import ssl

class WDPBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("WDP Browser Professional")
        self.root.geometry("1024x768")

        # Config
        self.registry_file = "wdp_registry.json"
        self.registry = self.load_registry()

        # UI Components
        self.setup_ui()

        # History and State
        self.current_url = ""
        self.image_refs = [] # To prevent GC

    def load_registry(self):
        if os.path.exists(self.registry_file):
            with open(self.registry_file, "r") as f:
                return json.load(f)
        return {}

    def setup_ui(self):
        # Top Bar (Address Bar)
        self.nav_frame = ttk.Frame(self.root)
        self.nav_frame.pack(fill=tk.X, padx=10, pady=10)

        self.url_entry = ttk.Entry(self.nav_frame, font=("Segoe UI", 12))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.url_entry.insert(0, "wdp://x1co.com.br")
        self.url_entry.bind("<Return>", lambda e: self.navigate())

        self.go_btn = ttk.Button(self.nav_frame, text="Navigate", command=self.navigate)
        self.go_btn.pack(side=tk.LEFT, padx=5)

        # Content Area
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.text_area = tk.Text(self.main_container, wrap=tk.WORD, font=("Segoe UI", 11), padx=20, pady=20)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.main_container, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # Configure Tags for WDL 2.0
        self.text_area.tag_configure("title", font=("Segoe UI", 24, "bold"), spacing1=15, spacing3=15, foreground="#2c3e50")
        self.text_area.tag_configure("text", spacing1=8, font=("Segoe UI", 12))
        self.text_area.tag_configure("link", foreground="#3498db", underline=True, font=("Segoe UI", 12, "bold"))
        self.text_area.tag_configure("error", foreground="#e74c3c", font=("Consolas", 12))
        self.text_area.tag_configure("center", justify='center')

        # Bind link click
        self.text_area.tag_bind("link", "<Button-1>", self.on_link_click)
        self.text_area.tag_bind("link", "<Enter>", lambda e: self.text_area.config(cursor="hand2"))
        self.text_area.tag_bind("link", "<Leave>", lambda e: self.text_area.config(cursor=""))

    def resolve_host(self, host):
        return self.registry.get(host, host)

    def navigate(self):
        url = self.url_entry.get().strip()
        if not (url.startswith("wdp://") or url.startswith("wdps://")):
            url = "wdp://" + url
        self.fetch_url(url)

    def fetch_url(self, url):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.image_refs = [] 
        self.links = {}
        
        is_secure = url.startswith("wdps://")
        
        self.text_area.insert(tk.END, f"Connecting to {url}...\n", "center")
        self.root.update()

        try:
            # Parse URL: wdp://host:port/path?query
            match = re.match(r"(wdps?://)([^/?]+)([^?]*)(\?.*)?", url)
            if not match:
                raise Exception("The URL format is invalid. Try wdp://domain/path")
            
            proto, raw_host, path, query = match.groups()
            path = path or "/"
            query = query or ""
            
            # DNS/Registry Resolution
            host = self.resolve_host(raw_host)

            if ":" in host:
                host, port = host.split(":")
                port = int(port)
            else:
                port = 7071 if is_secure else 7070 

            # Connect and Request
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5) # Shorter timeout for better UX
                
                if is_secure:
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    s = context.wrap_socket(s, server_hostname=host)

                s.connect((host, port))
            except socket.timeout:
                raise Exception("Connection Timeout: The server took too long to respond. Is it running?")
            except socket.gaierror:
                raise Exception("Network Error: Could not resolve address. Are you connected to the internet?")
            except ConnectionRefusedError:
                raise Exception(f"Connection Refused: The server at {host}:{port} is not accepting connections.")
            except ssl.SSLError as se:
                raise Exception(f"SSL/Security Error: {se.reason if hasattr(se, 'reason') else str(se)}")
            except Exception as e:
                raise Exception(f"Connection Failed: {str(e)}")

            request = f"WDP {url}\r\n"
            s.sendall(request.encode('utf-8'))

            # Receive Response
            response = b""
            while True:
                chunk = s.recv(8192)
                if not chunk:
                    break
                response += chunk
            s.close()

            # Parse Response Header (Support WDP/1.0 and simple)
            header_end = response.find(b"\r\n\r\n")
            if header_end == -1: header_end = response.find(b"\n\n")
            
            header_text = response[:header_end].decode('utf-8')
            body = response[header_end+4:]

            lines = header_text.split("\r\n")
            first_line = lines[0].split(" ")
            
            # WDP/1.0 <STATUS> <MIMETYPE> or <STATUS> <MIMETYPE>
            if first_line[0] == "WDP/1.0":
                status_code = first_line[1]
                mimetype = first_line[2]
            else:
                status_code = first_line[0]
                mimetype = first_line[1]

            if status_code == "20":
                self.render(body, mimetype, url)
            else:
                self.render_error(f"Erro {status_code}: {body.decode('utf-8', 'ignore')}")

        except Exception as e:
            self.render_error(f"Erro de Rede: {str(e)}")
        
        self.text_area.config(state=tk.DISABLED)

    def render(self, body, mimetype, url):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.current_url = url

        if "text/wdl" in mimetype:
            self.render_wdl(body.decode('utf-8', 'ignore'))
        elif "text/html" in mimetype:
            self.render_html(body.decode('utf-8', 'ignore'))
        else:
            self.text_area.insert(tk.END, body.decode('utf-8', 'ignore'))

    def render_wdl(self, content):
        # Support for both [tag] (Legacy) and (tag) (EasyWDL)
        tokens = re.split(r"(\[.*?\]|\(.*?\))", content)
        current_tag = None
        active_link_url = None
        
        # Known tags for validation
        known_tags = {"title", "text", "image", "center", "link", "titulo", "texto", "imagem"}

        for token in tokens:
            is_tag = False
            tag_name = ""
            attrs = ""

            if (token.startswith("[") and token.endswith("]")) or \
               (token.startswith("(") and token.endswith(")")):
                
                tag_content = token[1:-1].strip()
                if tag_content.startswith("/"):
                    # Closing tag like [/text]
                    tmp_name = tag_content[1:].lower()
                    if tmp_name in known_tags or tmp_name == "wdl":
                        current_tag = None
                        continue
                
                parts = tag_content.split(" ", 1)
                tag_name = parts[0].lower()
                
                # Handle link:URL special case
                if ":" in tag_name:
                    tag_parts = tag_name.split(":", 1)
                    if tag_parts[0] in known_tags:
                        is_tag = True
                        tag_name = tag_parts[0]
                        active_link_url = tag_parts[1]
                elif tag_name in known_tags:
                    is_tag = True
                    attrs = parts[1] if len(parts) > 1 else ""

            if is_tag:
                # Same-tag closing logic: (text) ... (text)
                if tag_name == current_tag:
                    current_tag = None
                    continue
                
                current_tag = tag_name
                
                # Normalize tags to English
                if current_tag == "titulo": current_tag = "title"
                if current_tag == "texto": current_tag = "text"
                if current_tag == "imagem": current_tag = "image"

                if current_tag == "link" and not active_link_url:
                    url_match = re.search(r'url="(.*?)"', attrs)
                    active_link_url = url_match.group(1) if url_match else None
                
                if current_tag == "image":
                     url_match = re.search(r'src="(.*?)"', attrs)
                     if url_match:
                         self.insert_image(url_match.group(1))
            else:
                # It's content (or a parentheses that isn't a tag)
                if not token: continue # Skip empty splits
                
                # If we have an active image tag and no explicit src, 
                # use the content as the URL
                if current_tag == "image" and token.strip() and "://" in token:
                    self.insert_image(token.strip())
                    current_tag = None
                    continue

                if not current_tag:
                    # Text outside any tag is treated as normal text
                    self.text_area.insert(tk.END, token)
                elif current_tag == "title":
                    self.text_area.insert(tk.END, token, ("title", "center"))
                elif current_tag == "text":
                    self.text_area.insert(tk.END, token, "text")
                elif current_tag == "link":
                    start_idx = self.text_area.index(tk.INSERT)
                    self.text_area.insert(tk.END, token, "link")
                    end_idx = self.text_area.index(tk.INSERT)
                    self.links[f"{start_idx}-{end_idx}"] = active_link_url
                elif current_tag == "center":
                    self.text_area.insert(tk.END, token, "center")
                
                # If it's a block-level tag, ensure we have a newline IF the token had one
                # or just add it to keep it clean. But let's respect original formatting.

    def insert_image(self, url):
        try:
            url = url.strip()
            if url.startswith("http"):
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                img_data = response.content
            else:
                return

            img = Image.open(io.BytesIO(img_data))
            img.thumbnail((600, 400))
            photo = ImageTk.PhotoImage(img)
            self.image_refs.append(photo)
            self.text_area.image_create(tk.END, image=photo)
            self.text_area.insert(tk.END, "\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"[Erro na imagem ({url}): {str(e)}]\n", "error")

    def render_html(self, content):
        clean = re.sub(r'<.*?>', '', content)
        self.text_area.insert(tk.END, "[Aviso: Renderização HTML limitada]\n", "error")
        self.text_area.insert(tk.END, clean)

    def render_error(self, msg):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Ocorreu um erro ao carregar a página:\n\n", "center")
        self.text_area.insert(tk.END, msg, "error")

    def on_link_click(self, event):
        idx = self.text_area.index(f"@{event.x},{event.y}")
        tags = self.text_area.tag_names(idx)
        if "link" in tags:
            for key, url in self.links.items():
                start, end = key.split("-")
                if self.text_area.compare(idx, ">=", start) and self.text_area.compare(idx, "<=", end):
                    self.url_entry.delete(0, tk.END)
                    self.url_entry.insert(0, url)
                    self.navigate()
                    break

def main():
    root = tk.Tk()
    app = WDPBrowser(root)
    root.mainloop()

if __name__ == "__main__":
    main()
