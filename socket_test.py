# https://gist.github.com/lrvick/1185629

from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import Flask, request

app = Flask('socket_test')

@app.route('/')
def root_handler():
    return 'Hello from the server!'


@app.route('/echo')
def echo_ws_handler():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        print(f'Incoming websocket: {repr(ws)}')
        message = ws.receive()
        print(f'Message received: {message}')
        ws.send(message)
    else:
        print('Couldn''t establish websocket connection.')
    return 'dummy return'


def main():
    server = WSGIServer(('', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
