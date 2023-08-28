import socket
import threading
import time
import pickle
import cv2
import struct
import time
import yaml


def send_data(conn, payload, data_id=0):
    """
    @brief: send payload along with data size and data identifier to the connection
    @args[in]:
        conn: socket object for connection to which data is supposed to be sent
        payload: payload to be sent
        data_id: data identifier
    """
    # serialize payload
    serialized_payload = pickle.dumps(payload)
    # send data size, data identifier and payload
    conn.sendall(struct.pack(">I", len(serialized_payload)))
    conn.sendall(struct.pack(">I", data_id))
    conn.sendall(serialized_payload)


def receive_data(conn):
    """
    @brief: receive data from the connection assuming that
        first 4 bytes represents data size,
        next 4 bytes represents data identifier and
        successive bytes of the size 'data size'is payload
    @args[in]:
        conn: socket object for conection from which data is supposed to be received
    """
    # receive first 4 bytes of data as data size of payload
    data_size = struct.unpack(">I", conn.recv(4))[0]
    # receive next 4 bytes of data as data identifier
    data_id = struct.unpack(">I", conn.recv(4))[0]
    # receive payload till received payload size is equal to data_size received
    received_payload = b""
    reamining_payload_size = data_size
    while reamining_payload_size != 0:
        received_payload += conn.recv(reamining_payload_size)
        reamining_payload_size = data_size - len(received_payload)
    payload = pickle.loads(received_payload)
    return (data_id, payload)


def handle_client(conn, conn_name, config):
    """
    @brief: handle the connection from client at seperate thread
    @args[in]:
        conn: socket object of connection
        con_name: name of the connection
    """
    cam_buffer = []
    timer = time.time()
    while True:
        data_id, payload = receive_data(conn)
        # if data identifier is image then handle the image
        if data_id == config["data_identifiers"]["image"]:
            # show normal cam
            if config["server"]["show_normal_cam"]:
                cv2.imshow("normal_stream", payload)
            # show cam with latency
            if config["server"]["show_cam_with_latency"]:
                if len(cam_buffer) > config["server"]["cam_buffer_len"]:
                    cam_buffer = []
                cam_buffer.append(payload)
                current_time = time.time()
                if current_time - timer > config["server"]["latency"]:
                    cv2.imshow("stream_with_latency", cam_buffer[0])
                    cam_buffer.pop(0)
                    cv2.waitKey(1)
                    timer = current_time
            # send response to client
            send_data(conn, "Image received on server")
        else:
            # if data is 'bye' then break the loop and client connection will be closed
            if payload == "bye":
                print("[INFO]: {} requested to close the connection".format(conn_name))
                print("[INFO]: Closing connection with {}".format(conn_name))
                break
            else:
                print(payload)
    conn.close()
    cv2.destroyAllWindows()


def main(config):
    # create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((config["ip"], config["port"]))
    server_socket.listen(5)
    print("[INFO]: Server Started")

    while True:
        try:
            # accept client connection
            # if first message from client match the defined message
            # then handle it at separate thread
            # otherwise close the connection
            conn, (address, port) = server_socket.accept()
            conn_name = "{}|{}".format(address, port)
            print("[INFO]: Accepted the connection from {}".format(conn_name))
            first_payload = receive_data(conn)[1]
            if first_payload == config["key_message"]:
                print("Connection could be trusted, starting communication")
                send_data(conn, "Connection accepted")
                threading.Thread(
                    target=handle_client,
                    args=(conn, conn_name, config),
                ).start()
                break
            else:
                print(
                    "[WARNING]: Accepted connection is an unknown client, \
                      closing the connection"
                )
                send_data(conn, "You are not authorized")
                conn.close()
        # break the while loop when keyboard interrupt is received and server will be closed
        except KeyboardInterrupt:
            print("\n[INFO]: Keyboard Interrupt Received")
            break
    server_socket.close()
    # print("[INFO]: Server Closed")


if __name__ == "__main__":
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    main(config)
