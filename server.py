import socket
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
clients = []
connected_clients = {}
chat_rooms = {}
clients_lock = threading.Lock()
def create_id():
    return str(uuid.uuid4())


def handle_client(client_socket, user_id):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8').strip()
            print(f"message : {message}")
            if not message:
                break
            
            if message.startswith("/create"):
                _, target_user = message.split()
                room_id = tuple(sorted([user_id, target_user]))
                chat_rooms[room_id] = [client_socket, connected_clients[target_user]]
                client_socket.send(f"private chat created with {target_user}".encode('utf-8'))
            
            elif message.startswith("/join"):
                _, target_user = message.split()
                room_id = tuple(sorted([user_id, target_user]))
                if room_id in chat_rooms:
                    chat_rooms[room_id].append(client_socket)
                    client_socket.send(f"Joined private chat with {target_user}.".encode('utf-8'))
                else:
                    client_socket.send(f"No private chat with {target_user}".encode('utf-8'))
            else:
                for room_id, room_clients in chat_rooms.items():
                    if client_socket in room_clients:
                        for client in room_clients:
                            if client != client_socket:
                                client.send(f"{user_id}: {message}".encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            del connected_clients[user_id]
            break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 9999))
server.listen(5)
print("Server started on port 9999")
client_socket, client_address = server.accept()
user_id = str(client_socket.recv(1024).decode('utf-8')).strip()
print(f"active threads: {threading.active_count()}")
with ThreadPoolExecutor(max_workers=10) as executor:
    while True:
        client_socket, client_address = server.accept()
        print(f"Active threads: {threading.active_count()}")
        try:
            user_id = str(client_socket.recv(1024).decode('utf-8')).strip()
        except Exception as e:
            print(f"Error receiving user ID: {e}")
            client_socket.close()
            continue
        with clients_lock:
            if user_id == "None":
                user_id = create_id()
                connected_clients[user_id] = client_socket
                client_socket.send(f"Your user_id is: {user_id}".encode('utf-8'))
                print(f"Accepted connection from new user {user_id}")
            else:
                if user_id in connected_clients:
                    client_socket.send(f"Welcome back {user_id}".encode('utf-8'))
                    print(f"Accepted reconnection from {user_id}")
                else:
                    connected_clients[user_id] = client_socket
                    client_socket.send(f"New user registered with ID: {user_id}".encode('utf-8'))
                    print(f"Accepted new connection from {user_id}")
        clients.append(client_socket)
        executor.submit(handle_client, client_socket, user_id)
