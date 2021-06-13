# This version will create zombies process because when it forks it doesn't wait for the child process to finish
import os
import socket
import time

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5


def handle_request(client_connection):
    request = client_connection.recv(1024)
    print(
        'Child PID: {pid}. Parent PID {ppid}'.format(
            pid=os.getpid(),
            ppid=os.getppid(),
        )
    )
    print(request.decode())
    http_response = b"""\
HTTP/1.1 200 OK

Hello, World!
"""
    client_connection.sendall(http_response)
    time.sleep(60)
    print(f"Close collection from child")


def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))
    print('Parent PID (PPID): {pid}\n'.format(pid=os.getpid()))

    while True:
        client_connection, client_address = listen_socket.accept()
        print(f"New request from: {client_address}")
        pid = os.fork() # immediately fork process at this point
        if pid == 0:  # child
            print(f"New client {os.getpid()}")
            listen_socket.close()  # close child copy
            handle_request(client_connection)
            client_connection.close()
            os._exit(0)  # child exits here
        else:  # parent
            print(f"Close client {os.getpid()}")
            client_connection.close()  # close parent copy and loop over
            # This close call is actually terminal the reference to fd of that connection
            # Because when the os forks, it also forks the reference to the connection and one will reside in the child process
            # When ever the child process close that reference => the connection will actually be terminated

if __name__ == '__main__':
    serve_forever()
