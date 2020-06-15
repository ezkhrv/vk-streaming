import asyncio
import argparse
import websockets
import logging
import json
from stream import Stream

async def handler(websocket, output):
    async for message in websocket:
        output.write(message + "\n")

async def consume(url, output):
    while True:
        try:
            async with websockets.connect(url) as websocket:
                await handler(websocket, output)
        except websockets.exceptions.ConnectionClosedError as err:
            logging.error(f"Websocket closed connection with error:\"{str(err)}\". Reconnecting")

def set_rules(stream, words):
    rules = stream.get_rules()
    logging.info(f'Current rules:{json.dumps(rules, ensure_ascii=False)}')
    logging.info('Deleting current rules')
    for rule in rules:
        stream.delete_rule(rule)
    logging.info('Setting new rules')
    for word in words:
        stream.add_rule(word)
    rules = stream.get_rules()
    logging.info(f'New rules:{json.dumps(rules, ensure_ascii=False)}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reading vk stream')
    parser.add_argument('--token', required=True, help='vk application token')
    parser.add_argument('--output', required=True, help='path to output file')
    parser.add_argument('--rules', required=True, help='comma-separated list of words to track')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    with open(args.token) as f:
        token = f.read().strip()
    stream = Stream(token)
    set_rules(stream, args.rules.split(','))

    loop = asyncio.get_event_loop()
    with open(args.output, 'w') as out_file:
        loop.run_until_complete(consume(stream.get_stream_url(), out_file))
