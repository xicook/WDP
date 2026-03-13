import socket
import threading
import os
import mimetypes
import ssl

PORT = 7070
SECURE_PORT = 7071
WWW_DIR = "www"
CERT_FILE = "server.pem" # Combined crt and key

# Custom MIMETYPE for WDL
mimetypes.add_type('text/wdl', '.wdl')

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024).decode('utf-8').strip()
        if not data.startswith("WDP "):
            client_socket.close()
            return

        # Extract URL or Path
        raw_path = data[4:].strip()
        if raw_path.startswith("wdp://") or raw_path.startswith("wdps://"):
            # Remove protocol
            clean_path = re.sub(r"wdps?://[^/]+", "", raw_path)
            path = clean_path if clean_path else "/"
        else:
            path = raw_path

        if path == "/" or path == "":
            path = "/index.wdl"

        file_path = os.path.join(WWW_DIR, path.lstrip("/"))
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            mimetype, _ = mimetypes.guess_type(file_path)
            if not mimetype:
                mimetype = "text/plain"
            
            with open(file_path, "rb") as f:
                content = f.read()
            
            # WDP/1.0 Protocol Header
            header = f"WDP/1.0 20 {mimetype}\r\nContent-Length: {len(content)}\r\n\r\n"
            client_socket.sendall(header.encode('utf-8') + content)
            print(f"[WDP/1.0] Served: {path} ({mimetype})")
        else:
            response = "WDP/1.0 40 text/plain\r\n\r\nFile Not Found".encode('utf-8')
            client_socket.sendall(response)
            print(f"[WDP/1.0] Not Found: {path}")

    except Exception as e:
        print(f"Error: {e}")
        response = "WDP/1.0 50 text/plain\r\n\r\nServer Error".encode('utf-8')
        client_socket.sendall(response)
    finally:
        client_socket.close()

import re # Needed for path parsing

def start_server(port, secure=False):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(10)
    
    mode = "WDPS (SECURE)" if secure else "WDP"
    print(f"{mode} Server running on port {port}...")

    if secure:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        if os.path.exists(CERT_FILE):
            context.load_cert_chain(certfile=CERT_FILE)
        else:
            print("Warning: server.pem not found. Secure mode might fail.")
    
    while True:
        client, addr = server.accept()
        if secure:
            try:
                client = context.wrap_socket(client, server_side=True)
            except Exception as e:
                print(f"SSL Handshake Error: {e}")
                client.close()
                continue
        
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def main():
    if not os.path.exists(WWW_DIR):
        os.makedirs(WWW_DIR)

    # Start normal WDP
    threading.Thread(target=start_server, args=(PORT, False), daemon=True).start()
    
    # Start WDPS
    start_server(SECURE_PORT, True)

if __name__ == "__main__":
    main()
