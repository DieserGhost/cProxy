import socket
import threading
from blacklist import load_blacklist
from utils import safe_print

BLOCKED_DOMAINS = load_blacklist()

def forward(source, destination):
    try:
        while True:
            data = source.recv(4096)
            if not data:
                break
            destination.sendall(data)
    except Exception:
        pass

def handle_client(client_socket):
    global BLOCKED_DOMAINS
    try:
        request = client_socket.recv(4096)
        if not request:
            client_socket.close()
            return

        try:
            request_str = request.decode('utf-8', errors='ignore')
        except Exception:
            client_socket.close()
            return

        if request_str.startswith("CONNECT"):
            first_line = request_str.split("\n")[0]
            parts = first_line.split(" ")
            if len(parts) < 2:
                client_socket.close()
                return
            target = parts[1]
            try:
                target_host, target_port = target.split(":")
                target_port = int(target_port)
            except Exception:
                client_socket.close()
                return

            for blocked in BLOCKED_DOMAINS:
                if target_host.endswith(blocked):
                    response = "HTTP/1.1 403 Forbidden\r\n\r\n"
                    client_socket.send(response.encode('utf-8'))
                    client_socket.close()
                    safe_print(f"❌ Blocked: {target_host}")
                    return

            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((target_host, target_port))
            client_socket.send(b"HTTP/1.1 200 Connection established\r\n\r\n")
            safe_print(f"✅ Allowed: {target_host}:{target_port}")

            # Starte Threads, um Daten in beide Richtungen weiterzuleiten
            t1 = threading.Thread(target=forward, args=(client_socket, remote_socket))
            t2 = threading.Thread(target=forward, args=(remote_socket, client_socket))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

            remote_socket.close()
            client_socket.close()
        else:
            host = None
            for line in request_str.split("\r\n"):
                if line.lower().startswith("host:"):
                    host = line.split(":", 1)[1].strip()
                    break

            if not host:
                client_socket.close()
                return

            port = 80
            if ":" in host:
                host, port_str = host.split(":", 1)
                port = int(port_str)

            for blocked in BLOCKED_DOMAINS:
                if host.endswith(blocked):
                    response = (
                        "HTTP/1.1 403 Forbidden\r\n"
                        "Content-Type: text/plain\r\n"
                        "Content-Length: 15\r\n"
                        "\r\n"
                        "Access Denied!\n"
                    )
                    client_socket.send(response.encode('utf-8'))
                    client_socket.close()
                    safe_print(f"❌ Blocked: {host}")
                    return

            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((host, port))
            remote_socket.sendall(request)
            safe_print(f"✅ Allowed HTTP request to: {host}:{port}")

            while True:
                data = remote_socket.recv(4096)
                if not data:
                    break
                client_socket.sendall(data)

            remote_socket.close()
            client_socket.close()
    except Exception as e:
        safe_print("Fehler:", e)
        client_socket.close()

def start_proxy(listen_port=8888):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", listen_port))
    server.listen(100)
    safe_print(f"Proxy running on Port: {listen_port} ...")
    try:
        while True:
            client_socket, addr = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.daemon = True
            client_handler.start()
    except KeyboardInterrupt:
        safe_print("Proxy getting closed..")
        server.close()
