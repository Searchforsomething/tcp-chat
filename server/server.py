import logging
import os
import re
import signal
import socket
import sys
import threading

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

USERNAME_REGEX = re.compile(r'^[A-Za-z0-9_]{3,20}$')


def is_valid_username(username):
    return USERNAME_REGEX.match(username) is not None


def is_valid_message_format(message):
    return ':' in message and len(message.split(':', 1)[1].strip()) > 0


def handle_client(conn, addr):
    username = None
    try:
        while not shutting_down:
            conn.sendall(b'Enter your username: \n')
            username = conn.recv(1024).decode().strip()

            with clients_lock:
                if not username or not is_valid_username(username):
                    conn.sendall(b'Invalid username. Use 3-20 letters, numbers, or underscores.\n')
                    continue
                if username in clients:
                    conn.sendall(b'Username already in use.\n')
                    continue
                clients[username] = conn
                break

        logging.info(f'{username} connected from {addr}')
        conn.sendall(b'Welcome! You can now send messages.\nFormat: recipient: message\n')

        while not shutting_down:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode().strip()
            if not is_valid_message_format(message):
                conn.sendall(b'Invalid format. Use: recipient: message\n')
                continue

            recipient, text = map(str.strip, message.split(':', 1))

            with clients_lock:
                target = clients.get(recipient)

            if target:
                try:
                    safe_text = text.replace('\n', ' ').replace('\r', ' ')
                    target.sendall(f'{username}: {safe_text}\n'.encode())
                    conn.sendall(b'Message delivered.\n')
                    logging.info(f'{username} -> {recipient}: {safe_text}')
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
                conn.shutdown(socket.SHUT_RDWR)
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
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    try:
        while True:
            conn, addr = server_socket.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
            client_threads.append(t)
    except OSError:
        pass


if __name__ == '__main__':
    main()
