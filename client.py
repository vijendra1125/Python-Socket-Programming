import socket
import pickle
import cv2
import struct


def send_data(conn, payload, data_id=0):
    '''
    @brief: send payload along with data size and data identifier to the connection
    @args[in]:
        conn: socket object for connection to which data is supposed to be sent
        payload: payload to be sent
        data_id: data identifier
    '''
    # serialize payload
    serialized_payload = pickle.dumps(payload)
    # send data size, data identifier and payload
    conn.sendall(struct.pack('>I', len(serialized_payload)))
    conn.sendall(struct.pack('>I', data_id))
    conn.sendall(serialized_payload)


def receive_data(conn):
    '''
    @brief: receive data from the connection assuming that 
        first 4 bytes represents data size,  
        next 4 bytes represents data identifier and 
        successive bytes of the size 'data size'is payload
    @args[in]: 
        conn: socket object for conection from which data is supposed to be received
    '''
    # receive first 4 bytes of data as data size of payload
    data_size = struct.unpack('>I', conn.recv(4))[0]
    # receive next 4 bytes of data as data identifier
    data_id = struct.unpack('>I', conn.recv(4))[0]
    # receive payload till received payload size is equal to data_size received
    received_payload = b""
    reamining_payload_size = data_size
    while reamining_payload_size != 0:
        received_payload += conn.recv(reamining_payload_size)
        reamining_payload_size = data_size - len(received_payload)
    payload = pickle.loads(received_payload)
    return (data_id, payload)


# define category in which you would like to define data
data_identifiers = {'info': 0, 'data': 1, 'image': 2}
# key to be trusted by server
key_message = 'C0nn3c+10n'
# a sample dictionary data
data = {'data number': 0,
        'message': 'A new message has been arrived from client'}


def main():
    # create client socket object and connect it to server
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(('127.0.0.1', 12345))
    send_data(conn, key_message)
    first_payload = receive_data(conn)[1]
    if first_payload == 'You are not authorized':
        print('[ERROR]: Access denied')
    else:
        # send a dictionary data and image data in loop till keyboard interrupt is received
        while True:
            try:
                # send dict
                data['data number'] += 1
                send_data(conn, data, data_identifiers['data'])
                print(receive_data(conn)[1])
                # send image
                image = cv2.imread('client_data/sample_image.png', 0)
                send_data(conn, image, data_identifiers['image'])
                print(receive_data(conn)[1])
            except KeyboardInterrupt:
                print(receive_data(conn)[1])
                print('\n[INFO]: Keyboard Interrupt received')
                break
        # once keyboard interrupt is received, send signal to server for closing connection
        send_data(conn, 'bye')
        print(receive_data(conn)[1])
    # close connection
    conn.close()
    print('[INFO]: Connection closed')


if __name__ == '__main__':
    main()
