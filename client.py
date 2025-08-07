import socket
import threading
import time
def receive_message(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except Exception as e:
            print(f"Error in receive_message: {e}")
            client_socket.close()
            break

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("connecting to the server...")
    client.connect(("127.0.0.1", 9999))
    user_id = input("Enter your user ID(leave it blank if you don't have any): ")
    if user_id:
        client.send(user_id.encode('utf-8'))
    else:
        user_id = "None"
        client.send(user_id.encode('utf-8'))
    receive_thread = threading.Thread(target=receive_message, args=(client,) )
    receive_thread.start()
    while True:
        message = input("you: ")
        client.send(message.encode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
    client.close()
