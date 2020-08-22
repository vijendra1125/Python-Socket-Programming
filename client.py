import socket
import pickle
import cv2
import struct


def send_data(conn, data, data_type=0):
    '''
    @brief: send data along with data size type to the connection
    @args[in]:
        conn: socket object for connection to which data is supposed to be sent
        data: data to be sent
        type: type of data to be sent
    '''
    # serialize data
    serialized_data = pickle.dumps(data)
    # send data size, data type and payload
    conn.sendall(struct.pack('>I', len(serialized_data)))
    conn.sendall(struct.pack('>I', data_type))
    conn.sendall(serialized_data)


def receive_data(conn):
    '''
    @brief: receive data from the connection assuming that 
        first 4 bytes represents data size,  
        next 4 bytes represents data type and 
        successive bytes of the size 'data size'is payload
    @args[in]: 
        conn: socket object for conection from which data is supposed to be received
    '''
    # receive first 4 bytes of data as data size of payload
    data_size = struct.unpack('>I', conn.recv(4))[0]
    # receive next 4 bytes of data as data type
    data_type = struct.unpack('>I', conn.recv(4))[0]
    # receive payload till received payload size is equal to data_size received
    received_payload = b""
    reamining_payload_size = data_size
    while reamining_payload_size != 0:
        received_payload += conn.recv(reamining_payload_size)
        reamining_payload_size = data_size - len(received_payload)
    data = pickle.loads(received_payload)
    return (data_type, data)


# servers to be conected with
server_address = {'server1': ('192.168.1.2', 12345)}
# define category in which you would like to define data
data_types = {'info': 0, 'data': 1, 'image': 2}


def main():
    # create client socket object and connect it to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address['server1'])

    # send a dictionary and image data in loop till keyboard interrupt is received
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
    # once keyboard interrupt is received, send signal to serer for closing connection
    # and close client socket
    send_data(client_socket, 'bye')
    print(receive_data(client_socket)[1])
    client_socket.close()


if __name__ == '__main__':
    main()
