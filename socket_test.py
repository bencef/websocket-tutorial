# https://gist.github.com/lrvick/1185629

import gevent
from collections import namedtuple
from flask import Flask, request, make_response, render_template
from gevent.pywsgi import WSGIServer
from gevent.queue import Channel
from geventwebsocket.exceptions import WebSocketError
from geventwebsocket.handler import WebSocketHandler

app = Flask('socket_test')
comm_channel = Channel()
Message = namedtuple('Message', ['tag', 'payload'])
Subscribe = namedtuple('Subscribe', ['socket'])
IncomingMessage = namedtuple('IncomingMessage', ['sender', 'text'])

@app.route('/')
def root_handler():
    return render_template('index.html')


@app.route('/echo')
def echo_ws_handler():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        global comm_channel
        comm_channel.put(Message(tag='Subscribe', payload=Subscribe(ws)))
        print(f'Incoming websocket: {repr(ws)}')
        try:
            while True:
                message = ws.receive()
                print(f'Message received: {message}')
                comm_channel.put(Message(tag='IncomingMessage',
                                         payload=IncomingMessage(sender='Anon', text=message)))
        except WebSocketError:
            return ''
    else:
        print('Couldn''t establish websocket connection.')
    bad_request = 400
    return make_response('Only wbsockets supported on this endpoint', bad_request)


def broadcast_handler():
    global comm_channel
    connections = set()
    while True:
        msg = comm_channel.get()
        if msg.tag == 'Subscribe':
            connections.add(msg.payload.socket)
        elif msg.tag == 'IncomingMessage':
            sender = msg.payload.sender
            text = msg.payload.text
            to_remove = []
            for ws in connections:
                try:
                    ws.send(f'{sender}: {text}')
                except WebSocketError:
                    to_remove.append(ws)
            for ws in to_remove:
                connections.remove(ws)
        else:
            print(f'Unknown message type: {msg.tag}')


def main():
    gevent.spawn(broadcast_handler)
    server = WSGIServer(('', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
