import socket
import pickle
import cv2
import struct


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


data_types = {'info': 0, 'data': 1, 'image': 2}
server_address = {'server1': ('192.168.1.2', 12345)}


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address['server1'])
    data = {'data number': 0,
            'message': 'A new message has been arrived from client'}
    while True:
        try:
            data['data number'] += 1
            send_data(client_socket, data, data_types['data'])
            print(receive_data(client_socket)[1])
            image = cv2.imread('client_data/sample_image.png', 0)
            send_data(client_socket, image, data_types['image'])
            print(receive_data(client_socket)[1])
        except KeyboardInterrupt:
            print(receive_data(client_socket)[1])
            print('\n---Keyboard Interrupt received---')
            break

    send_data(client_socket, 'bye')
    print(receive_data(client_socket)[1])
    client_socket.close()


if __name__ == '__main__':
    main()
