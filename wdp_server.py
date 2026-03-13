import socket
import threading
import os
import mimetypes

PORT = 7070
WWW_DIR = "www"

# Custom MIMETYPE for WDL
mimetypes.add_type('text/wdl', '.wdl')

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024).decode('utf-8').strip()
        if not data.startswith("WDP "):
            print(f"Invalid request: {data}")
            client_socket.close()
            return

        # Extract URL or Path
        raw_path = data[4:].strip()
        if raw_path.startswith("wdp://"):
            parts = raw_path.replace("wdp://", "").split("/", 1)
            path = "/" + (parts[1] if len(parts) > 1 else "")
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

def main():
    if not os.path.exists(WWW_DIR):
        os.makedirs(WWW_DIR)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind to all interfaces to allow remote access
    server.bind(("0.0.0.0", PORT))
    server.listen(10)
    print(f"WDP/1.0 Professional Server running on all interfaces, port {PORT}...")

    while True:
        client, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    main()
