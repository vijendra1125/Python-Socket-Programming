import socket
import threading
import time
import pickle
import cv2
import struct

# add only the devices you want to communicate with
trusted_clients = {'127.0.0.1': 'client1'}
# define category in which you would like to define data
data_types = {'info': 0, 'data': 1, 'image': 2}


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


def do_something(conn_name, data):
    '''
    @beief: a sample function to do something with received data
    @args[in]:
        conn_name: connection name from where dat is received
        data: received data
    @args[out]:
        a string response
    '''
    print('Data number {} received from client {}'.format(
        data['data number'], conn_name))
    time.sleep(0.1)
    return 'Data number {} received on server'.format(data['data number'])


def handle_client(conn, conn_name):
    '''
    @brief: handle the connection from client at seperate thread
    @args[in]:
        conn: socket object of connection 
        con_name: name of the connection
    '''
    while True:
        data_type, data = receive_data(conn)
        # if data type is image then save the image
        if data_type == data_types['image']:
            print('---Recieved image too ---')
            cv2.imwrite('server_data/received_image.png', data)
            send_data(conn, 'Image received on server')
        # otherwise send the data to do something
        elif data_type == data_types['data']:
            response = do_something(conn_name, data)
            send_data(conn, response)
        else:
            # if data is 'bye' then break the loop and client connection will be closed
            if data == 'bye':
                print('{} requested to close the connection'.format(conn_name))
                print('Closing connection with {}'. format(conn_name))
                send_data(conn, 'You are disconnected from server now')
                break
            else:
                print(data)
    conn.close()


def main():
    # create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 12345
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(5)
    print('---Server Started---')

    while True:
        try:
            # accept client connection
            # if its trusted  then handle it at seperate thread
            # otherwise close connection imediately
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
        # break the while loop when keyboard intterupt is received and server will be closed
        except KeyboardInterrupt:
            print('\n---Keyboard Interrupt Received---')
            break

    server_socket.close()
    print('---Server Closed---')


if __name__ == '__main__':
    main()
