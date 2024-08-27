#!/usr/bin/env python3

# imports
import asyncio
import email
import functools
import json
import logging
import names
import os
import pathlib
import random
import requests
import time
import websockets

from http import HTTPStatus
from pprint import pprint

SOCKETS = {}
MIME_TYPES = {
    "html": "text/html",
    "png":  "image/png",
    "jpg":  "image/jpg",
    "svg":  "image/svg+xml",
    "css":  "text/css",
    "js":   "application/x-javascript",
}

with open('config.json', 'r') as f:
    config = json.load(f)

# init
logging.basicConfig(level="INFO")

def generate_random_email_address():
    return names.get_first_name().lower() \
        + str(random.randrange(1000,9999)) \
        + "@" \
        random.choice(config['maildomains'])

async def message_controller(websocket, data):
    pass

async def connection_dispatcher(websocket, path):
    random_email = generate_random_email_address()
    logging.info("Random-Email: "+random_email)

    try:
        SOCKETS[random_email] = websocket
        await websocket.send('{"email_address":"'+random_email+'"}')
        async for message in websocket:
            try:
                data = json.loads(message)
            except Exception as e:
                logging.warning("Invalid client message:\n"+message+"\n"+str(e))

            await message_controller(websocket=websocket, data=data)
    finally:
        del SOCKETS[random_email]

async def process_request(server_root, path, request_headers):
    """Serves a file when doing a GET request with a valid path."""
    if "Upgrade" in request_headers:
        return  # Probably a WebSocket connection

    response_headers = [
        ('Server', 'tempmail'),
        ('Connection', 'close'),
    ]

    if path == '/':
        path = '/index.html'

    # Derive full system path
    full_path = str(pathlib.Path(os.path.join(server_root, path[1:])).absolute())

    # Validate the path
    if os.path.commonpath((server_root, full_path)) != server_root or \
            not os.path.exists(full_path) or not os.path.isfile(full_path):
        print("HTTP GET {} 404 NOT FOUND".format(path))
        return HTTPStatus.NOT_FOUND, [], b'404 NOT FOUND'

    # Guess file content type
    extension = full_path.split(".")[-1]
    if extension in MIME_TYPES:
        mime_type = MIME_TYPES[extension]
    else:
        mime_type = "application/octet-stream"
    response_headers.append(('Content-Type', mime_type))

    # Read the whole file into memory and send it out
    body = open(full_path, 'rb').read()
    response_headers.append(('Content-Length', str(len(body))))
    print("HTTP GET {} 200 OK".format(path))
    return HTTPStatus.OK, response_headers, body

async def tcp_email_receiver(reader, writer):
    data = await reader.read()
    myemail = email.message_from_bytes(data)

    if myemail["To"] in SOCKETS:
        await SOCKETS[myemail["To"]].send(json.dumps({"email": str(myemail)}))
    else:
        logging.info("No socket for recipient "+myemail["To"])

    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":

    handler = functools.partial(process_request, str(pathlib.Path(__file__).parent.absolute() / "public"))

    websocket_server = websockets.serve(
        connection_dispatcher,
        config['web']['listen_ip'],
        config['web']['listen_port'],
        process_request=handler)

    tcp_server = asyncio.start_server(
        tcp_email_receiver,
        config['tcp_email_receiver']['listen_ip'],
        config['tcp_email_receiver']['listen_port'])

    try:
        asyncio.get_event_loop().run_until_complete(websocket_server)
        asyncio.get_event_loop().run_until_complete(tcp_server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt as e:
        pass
