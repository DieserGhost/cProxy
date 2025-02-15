import threading
import proxy
import cli

def main():
    proxy_thread = threading.Thread(target=proxy.start_proxy, args=(8888,))
    proxy_thread.daemon = True
    proxy_thread.start()
    cli.start_cli()

if __name__ == '__main__':
    main()
