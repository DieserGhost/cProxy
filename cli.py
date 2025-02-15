import threading
import os
from blacklist import load_blacklist
import proxy
from utils import safe_print

def start_cli():
    while True:
        try:
            command = input("CLI> ").strip()
        except EOFError:
            continue

        if command == "blacklistrl":
            proxy.BLOCKED_DOMAINS = load_blacklist()
            safe_print("Blacklist reloaded!")
        elif command in ["exit", "quit"]:
            safe_print("Quitting Proxy and CLI")
            os._exit(0)
        else:
            safe_print("Unknown Command. available commands: blacklistrl, exit, quit")

def start_cli_thread():
    cli_thread = threading.Thread(target=start_cli)
    cli_thread.daemon = False
    cli_thread.start()
