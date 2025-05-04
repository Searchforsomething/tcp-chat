import os
import socket
import threading
import logging
import signal
import sys

HOST = '0.0.0.0'
PORT = 12345

clients = {}            
client_threads = []       
clients_lock = threading.Lock()
server_socket = None
shutting_down = False
shutdown_requested = False


logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


def handle_client(conn, addr):
    username = None
    try:
        while True:
            conn.sendall(b'Enter your username: \n')
            username = conn.recv(1024).decode().strip()

            with clients_lock:
                if not username or username in clients:
                    conn.sendall(b'Invalid or duplicate username.\n')
                    continue
                clients[username] = conn
                break

        logging.info(f'{username} connected from {addr}')
        conn.sendall(b'Welcome! You can now send messages.\nFormat: recipient: message\n')

        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode().strip()
            if ':' not in message:
                conn.sendall(b'Invalid format. Use: recipient: message\n')
                continue

            recipient, text = map(str.strip, message.split(':', 1))

            with clients_lock:
                target = clients.get(recipient)

            if target:
                try:
                    target.sendall(f'{username}: {text}\n'.encode())
                    conn.sendall(b'Message delivered.\n')
                    logging.info(f'{username} -> {recipient}: {text}')
                except:
                    conn.sendall(b'Failed to deliver message.\n')
            else:
                conn.sendall(b'Recipient not found.\n')

    finally:
        with clients_lock:
            if username in clients:
                del clients[username]
        conn.close()
        if username:
            logging.info(f'{username} disconnected')


def shutdown_server(signal_received=None, frame=None):
    global shutting_down, shutdown_requested

    if shutdown_requested:
        print('\nForce quitting...')
        os._exit(1)

    print('\nGracefully shutting down... (press Ctrl+C again to force)')
    shutdown_requested = True
    shutting_down = True

    if server_socket:
        server_socket.close()

    with clients_lock:
        for user, conn in clients.items():
            try:
                conn.sendall(b'Server is shutting down.\n')
                conn.close()
            except:
                pass
        clients.clear()

    for t in client_threads:
        t.join()

    print('Server shutdown complete.')
    sys.exit(0)


def main():
    global server_socket

    signal.signal(signal.SIGINT, shutdown_server)
    signal.signal(signal.SIGTERM, shutdown_server)

    print(f'Starting server on {HOST}:{PORT}...')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except OSError:
        pass  


if __name__ == '__main__':
    main()
