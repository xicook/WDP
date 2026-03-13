import socket
import threading
import json
import os
import re
from urllib.parse import unquote

SEARCH_PORT = 5555
REGISTER_PORT = 5060
INDEX_FILE = "search_index.json"
# Basic +18 filter (expandable)
BLOCKED_WORDS = {"porn", "sex", "hentai", "xxx", "adult", "nude", "naked"}

def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    return [
        {"name": "Register Me!", "url": "wdp://register.me", "description": "Register your site on WDP!"},
        {"name": "Search Me!", "url": "wdp://search.me", "description": "Global Search Engine for WDP."}
    ]

def save_index(index):
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=4)

def contains_blocked_content(text):
    text = text.lower()
    for word in BLOCKED_WORDS:
        if word in text:
            return True
    return False

def handle_client(client, port):
    try:
        data = client.recv(1024).decode('utf-8')
        if not data.startswith("WDP "):
            client.close()
            return
        
        request_line = data.split("\r\n")[0]
        url = request_line.split(" ")[1]
        
        # Parse query params: ?q=query or ?name=x&url=y&desc=z
        query_str = ""
        if "?" in url:
            query_str = url.split("?", 1)[1]
        
        params = {}
        if query_str:
            for pair in query_str.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[unquote(k)] = unquote(v)

        if port == SEARCH_PORT:
            response = handle_search(params)
        elif port == REGISTER_PORT:
            response = handle_register(params)
        else:
            response = "WDP/1.0 40 text/plain\r\n\r\nInvalid Port"

        client.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client.close()

def handle_search(params):
    q = params.get("q", "").lower()
    index = load_index()
    
    results = []
    if q:
        for site in index:
            if q in site['name'].lower() or q in site['description'].lower():
                results.append(site)
    else:
        results = index[:10] # Show some defaults if no query

    wdl = "(title) WDP Search Results (title)\n"
    wdl += f"(center) Showing results for: {q if q else 'Everything'} (center)\n\n"
    
    if not results:
        wdl += "(text) No results found. (text)\n"
    else:
        for site in results:
            wdl += f"(title) {site['name']} (title)\n"
            wdl += f"(text) {site['description']} (text)\n"
            wdl += f"(link:{site['url']}) Visit Site (link:{site['url']})\n\n"
    
    wdl += "\n(center) (link:wdp://search.me) New Search (link:wdp://search.me) (center)"
    
    return f"WDP/1.0 20 text/wdl\r\n\r\n{wdl}"

def handle_register(params):
    name = params.get("name")
    url = params.get("url")
    desc = params.get("desc")
    
    if not (name and url and desc):
        wdl = "(title) Register your WDP Site (title)\n"
        wdl += "(text) To register, use the URL parameters: name, url, and desc. (text)\n"
        wdl += "(text) Example: wdp://register.me?name=MySite&url=wdp://mysite&desc=Awesome (text)\n"
        return f"WDP/1.0 20 text/wdl\r\n\r\n{wdl}"

    # Validation
    if contains_blocked_content(name) or contains_blocked_content(desc) or contains_blocked_content(url):
        return "WDP/1.0 43 text/wdl\r\n\r\n(title) Error (title)\n(text) Content violates safety rules (+18 not allowed). (text)"

    if not (url.startswith("wdp://") or url.startswith("wdps://")):
        return "WDP/1.0 40 text/wdl\r\n\r\n(text) Invalid URL protocol. (text)"

    index = load_index()
    # Check if exists
    if any(s['url'] == url for s in index):
        return "WDP/1.0 20 text/wdl\r\n\r\n(text) Site already registered! (text)"

    index.append({"name": name, "url": url, "description": desc})
    save_index(index)
    
    return "WDP/1.0 20 text/wdl\r\n\r\n(title) Success! (title)\n(text) Your site has been registered in the WDP index. (text)"

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"Server started on port {port}")
    
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client, port)).start()

if __name__ == "__main__":
    t_search = threading.Thread(target=start_server, args=(SEARCH_PORT,))
    t_register = threading.Thread(target=start_server, args=(REGISTER_PORT,))
    
    t_search.start()
    t_register.start()
    
    t_search.join()
    t_register.join()
