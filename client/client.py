import socket
import threading
import sys
import select

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

stop_event = threading.Event()

def receive_messages(sock):
    try:
        while not stop_event.is_set():
            try:
                data = sock.recv(1024)
                if not data:
                    print('\nServer closed the connection.')
                    stop_event.set()
                    break
                print(data.decode(), end='')
            except socket.timeout:
                continue
            except (OSError, ConnectionResetError):
                stop_event.set()
                break
    finally:
        stop_event.set()

def send_messages(sock):
    try:
        while not stop_event.is_set():
            ready, _, _ = select.select([sys.stdin], [], [], 0.5)
            if ready:
                line = sys.stdin.readline()
                if not line:
                    break
                sock.sendall(line.encode())
            else:
                continue
    except (BrokenPipeError, OSError):
        pass
    finally:
        stop_event.set()

def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        sock.connect((SERVER_HOST, SERVER_PORT))
    except Exception as e:
        print(f'Failed to connect: {e}')
        return

    recv_thread = threading.Thread(target=receive_messages, args=(sock,))
    send_thread = threading.Thread(target=send_messages, args=(sock,))

    recv_thread.start()
    send_thread.start()

    try:
        while recv_thread.is_alive() or send_thread.is_alive():
            recv_thread.join(timeout=0.1)
            send_thread.join(timeout=0.1)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        stop_event.set()
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            sock.close()
        except:
            pass
        print('\nDisconnected.')

if __name__ == '__main__':
    main()
