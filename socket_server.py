import socket
import sys
import threading


subscribers={}
lock=threading.Lock()

def handle_client(conn, address):
    try:
        role_topic = conn.recv(1024).decode().strip().split(':')
        if len(role_topic) != 2:
            print(f"[!] Invalid client format from {address}")
            conn.send(b"Invalid format. Use publisher:topic or subscriber:topic")
            conn.close()
            return

        role, topic = role_topic
        role = role.lower().strip()
        topic = topic.lower().strip()

        print(f"[+] {role.capitalize()} connected from {address} with topic '{topic}'")

        if role == 'subscriber':
            with lock:
                if topic not in subscribers:
                    subscribers[topic] = []
                subscribers[topic].append(conn)

            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
            finally:
                with lock:
                    subscribers[topic].remove(conn)
                    if not subscribers[topic]:
                        del subscribers[topic]
                conn.close()

        elif role == 'publisher':
            try:
                while True:
                    message = conn.recv(1024).decode()
                    if not message:
                        break
                    print(f"[Publisher {address} | {topic}] {message}")
                    broadcast(topic, message)
            finally:
                conn.close()

        else:
            conn.send(b"Unknown role.")
            conn.close()

    except Exception as e:
        print(f"[!] Exception with {address}: {e}")
        conn.close()



def broadcast(topic, message): 
    with lock:
        if topic in subscribers:
            for sub_conn in list(subscribers[topic]):
                try:
                    sub_conn.send(f"[{topic}] {message}".encode())
                except:
                    subscribers[topic].remove(sub_conn)



def server_program():
    if len(sys.argv) < 2:
        print("Usage: python server.py <port>")
        return
    
    host = '127.0.0.1'
    port = int(sys.argv[1])

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(10)

    print(f"[*] Server running on {host}:{port}...")

    while True:
        conn, address = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, address), daemon=True).start()

if __name__ == '__main__':
    server_program()