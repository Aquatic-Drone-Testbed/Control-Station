import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)

usv_ip = '192.168.0.111'
server_address = (usv_ip, 30000)

try:
    while True:
        message = 'Ping'
        print(f"Sending: {message}")
        sock.sendto(message.encode(), server_address)
        
        try:
            data, server = sock.recvfrom(4096)
            print(f"Received response: {data.decode()}")
        except socket.timeout:
            print('REQUEST TIMED OUT')

finally:
    print("Closing socket")
    sock.close()
