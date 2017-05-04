#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import subprocess
import requests

from config import LoadBlocksConfig
config = LoadBlocksConfig

def zcash(cmd):
    zcash = subprocess.Popen([config.ZCASH_CLI_PATH, cmd], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = zcash.communicate()[0]
    try:
        json.loads(output)
    except Exception as e:
        print(e)
        print('Error: Can\'t communicate with Zcash RPC Interface.')
        return False
    return json.loads(output)

def get_block(block_height):
    zcash = subprocess.Popen([config.ZCASH_CLI_PATH, 'getblock', block_height], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = zcash.communicate()[0]
    try:
        json.loads(output)
    except Exception as e:
        print(e)
        print('Error: Can\'t retrieve block number ' + block_height + ' from zcashd.')
        return False
    return json.loads(output)

def main():
    number_of_blocks = zcash('getinfo')['blocks'] if zcash('getinfo') is not False else None
    if number_of_blocks is not None:
        session = requests.session()
        session.headers.update({'Content-Type': 'application/json'})
        for x in range(config.STARTING_BLOCK_HEIGHT if (config.STARTING_BLOCK_HEIGHT > 0) \
            else config.STARTING_BLOCK_HEIGHT, config.ENDING_BLOCK_HEIGHT \
            if (config.ENDING_BLOCK_HEIGHT < number_of_blocks) \
            else config.ENDING_BLOCK_HEIGHT):
                block = get_block(str(x))
                r = session.post(config.BLOCK_OBSERVATORY_URL, json=block)
                r.raise_for_status()
                print('Uploaded block ' + str(x) + '.')
    else:
        print('Error: Can\'t retrieve blocks from zcashd.')
        exit(1)
    exit(0)

if __name__ == '__main__':
    main()
