#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import subprocess
import requests

from config import LoadBlocksConfig
config = LoadBlocksConfig

def parse_cmd_args():
    description = """
Allows one to specify the block range to import via STARTING_BLOCK_HEIGHT and ENDING_BLOCK_HEIGHT
Examples:
     export STARTING_BLOCK_HEIGHT=1234
     export ENDING_BLOCK_HEIGHT=12345678
     ./loadblocks.py
"""
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--start', type=int, default=os.environ.get('STARTING_BLOCK_HEIGHT', 0), required=False, help="Block number to begin import from")
    parser.add_argument('--end', type=int, default=os.environ.get('ENDING_BLOCK_HEIGHT', None), required=False, help="Block number to stop importing at")
    return parser.parse_args()

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
    args = parse_cmd_args()
    is_zcashd_running()
    if not (args.start or args.end):
        start_point = config.STARTING_BLOCK_HEIGHT
        end_point = config.ENDING_BLOCK_HEIGHT
    number_of_blocks = zcash('getinfo')['blocks'] if zcash('getinfo') is not False else None
    if number_of_blocks is not None:
        session = requests.session()
        session.headers.update({'Content-Type': 'application/json'})
        for x in range(start_point if (start_point > 0) \
            else start_point, end_point \
            if (end_point < number_of_blocks) \
            else end_point):
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
