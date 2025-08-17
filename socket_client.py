import socket
import sys


def subscriber_mode(client_socket):
    try:
        while True:
            data=client_socket.recv(1024).decode()
            if not data:
                break
            print(data)
    except:
        print("Disconnected from server")
    finally:
        client_socket.close()
        
def publisher_mode(client_socket):
    try:
        while True:
            message=input("->")
            if message.lower().strip()=='terminate':
                break
            client_socket.send(message.encode())
    except:
        print("Disconnected from server.")
    finally:
        client_socket.close()


def client_program():
    if len(sys.argv) < 5:
        print("Invalid input")
        
        return

    host=sys.argv[1]
    port=int(sys.argv[2])
    role=sys.argv[3].lower()
    topic=sys.argv[4].lower()
    
    if role not in ['publisher','subscriber']:
        print("Invalid role.Use 'publisher' or 'subscriber'")
        return
    
    client_socket=socket.socket()
    client_socket.connect((host,port))
    client_socket.send(f"{role}:{topic}".encode())
    
    if role=='publisher':
        publisher_mode(client_socket)
    else:
        subscriber_mode(client_socket)
    
    
if __name__== '__main__':
    client_program()