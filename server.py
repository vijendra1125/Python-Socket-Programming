import socket
import threading
import time
import pickle
import cv2
import struct

# add only the devices you want to communicate with
trusted_clients = {'192.168.1.2': 'client1'}
data_types = {'info': 0, 'data': 1, 'image': 2}


def send_data(conn, data, data_type=0):
    serialized_data = pickle.dumps(data)
    conn.sendall(struct.pack('>I', len(serialized_data)))
    conn.sendall(struct.pack('>I', data_type))
    conn.sendall(serialized_data)


def receive_data(conn):
    data_size = struct.unpack('>I', conn.recv(4))[0]
    data_type = struct.unpack('>I', conn.recv(4))[0]

    received_payload = b""
    reamining_payload_size = data_size
    while reamining_payload_size != 0:
        received_payload += conn.recv(reamining_payload_size)
        reamining_payload_size = data_size - len(received_payload)
    data = pickle.loads(received_payload)

    return (data_type, data)


def do_something(conn_name, data):
    print('Data number {} received from client {}'.format(
        data['data number'], conn_name))
    # time.sleep(0.2)
    return 'Data number {} received on server'.format(data['data number'])


def handle_client(conn, conn_name):
    while True:
        data_type, data = receive_data(conn)
        if data_type == data_types['image']:
            print('---Recieved image---')
            cv2.imwrite('server_data/received_image.png', data)
            send_data(conn, 'Image received on server')
        elif data == 'bye':
            print('{} requested to close the connection'.format(conn_name))
            print('Closing connection with {}'. format(conn_name))
            send_data(conn, 'You are disconnected from server now')
            break
        else:
            response = do_something(conn_name, data)
            send_data(conn, response)
    conn.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 12345
    server_socket.bind(('', port))
    server_socket.listen(5)
    print('---Server Started---')

    while True:
        try:
            conn, (address, port) = server_socket.accept()
            conn_name = '{}_{}'.format(trusted_clients[address], port)
            if(address in list(trusted_clients.keys())):
                print("ACCEPTED the connection from {}".format(conn_name))
                threading.Thread(target=handle_client,
                                 args=(conn, conn_name)).start()
            else:
                print('REJECTING untrusted client with address {} and port {}'.format(
                    address, port))
                conn.close()
        except KeyboardInterrupt:
            print('\n---Keyboard Interrupt Received---')
            break

    server_socket.close()
    print('---Server Closed---')


if __name__ == '__main__':
    main()
