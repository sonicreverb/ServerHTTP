import socket
import os
import mimetypes

IP_ADDRESS = '127.0.0.1'
PORT = 8000
MAX_AWAITING_RESPONSES = 4

BASE_DIR = os.path.dirname(__file__)

HEADERS = {
    '200': 'HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n',
    '404': 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\n\r\n',
    '410': 'HTTP/1.1 410 Gone\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
}


def load_page_from_get_request(request_data):
    catalog = request_data.split(' ')[1][1:]
    if catalog == '':
        catalog = 'html/home.html'

    if catalog[:6] == 'secret':
        path = os.path.join(BASE_DIR, 'html/410_page.html')
        content_type = 'text/html; charset=utf-8'
        status_code = '410'
    else:
        path = os.path.join(BASE_DIR, catalog)
        if not os.path.exists(path):
            path = os.path.join(BASE_DIR, 'html/404_page.html')
            content_type = 'text/html; charset=utf-8'
            with open(path, 'rb') as file:
                response = HEADERS['404'].format(content_type).encode('utf-8') + file.read()
            return response

        content_type, _ = mimetypes.guess_type(path)
        status_code = '200'

    with open(path, 'rb') as file:
        response = HEADERS[status_code].format(content_type).encode('utf-8') + file.read()

    return response


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP_ADDRESS, PORT))
    print(f'SERVER STARTED AT {IP_ADDRESS}:{PORT}')
    server_socket.listen(MAX_AWAITING_RESPONSES)

    terminate = False

    while not terminate:
        client_socket, address = server_socket.accept()
        client_request = b''
        while True:
            chunk = client_socket.recv(1024)
            client_request += chunk
            if len(chunk) < 1024:
                break

        print(f'RECEIVED DATA: {client_request}')

        content = load_page_from_get_request(client_request.decode('utf-8'))
        client_socket.send(content)
        # print(f'SENT DATA: {content.decode("utf-8")}')
        client_socket.shutdown(socket.SHUT_WR)

    print('SERVER SHUTDOWN')


if __name__ == '__main__':
    main()
