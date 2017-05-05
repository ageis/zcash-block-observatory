#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import getpass
import os
import psutil
import subprocess
import sys
import requests

from config import LoadBlocksConfig
config = LoadBlocksConfig

def parse_cmd_args():
    description = """
Allows one to specify the block range to import via START_BLOCK_HEIGHT and END_BLOCK_HEIGHT
Example:
     export START_BLOCK_HEIGHT=1234
     export END_BLOCK_HEIGHT=12345678
     ./loadblocks.py
or...
     ./loadblocks.py --start 1234 --end 12345678
"""
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--start', type=int, default=os.environ.get('START_BLOCK_HEIGHT', 0), required=False, help="Block number to begin import from")
    parser.add_argument('--end', type=int, default=os.environ.get('END_BLOCK_HEIGHT', zcash('getblockcount')), required=False, help="Block number to stop importing at")
    return parser.parse_args()

def zcashd_access_test(proc):
    current_user = str(getpass.getuser())
    try:
        os.kill(proc['pid'], 0)
        if proc['username'] == current_user:
            print('Success: found zcashd is running as ' + current_user + ' allowing RPC interface access.')
            return True
    except Exception as e:
        print(e)
        print('Error: This zcashd does not seem to be running as the user of this script.')
        return False

def is_zcashd_running():
    zcashd_procs = filter(lambda p: p.name() == "zcashd", psutil.process_iter())
    if zcashd_procs is not [] and len(zcashd_procs) >= 1:
        procs = [proc.as_dict(attrs=['pid', 'username']) for proc in zcashd_procs]
        for proc in procs:
            print("zcashd running with pid %d as user %s" % (proc['pid'], proc['username']))
            while zcashd_access_test(proc):
                return True
    else:
        print('Error: Could not find an accessible running iinstance of zcashd on this system.')
        return False

def zcash(cmd):
    zcexec = subprocess.Popen([config.ZCASH_CLI_PATH, cmd], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = zcexec.communicate()[0]
    try:
        json.loads(output)
    except Exception as e:
        print(e)
        print('Error: Can\'t communicate with Zcash RPC Interface.')
        return False
    return json.loads(output)

def get_block(block_height):
    zcexec = subprocess.Popen([config.ZCASH_CLI_PATH, 'getblock', block_height], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = zcexec.communicate()[0]
    try:
        json.loads(output)
    except Exception as e:
        print(e)
        print('Error: Can\'t retrieve block number ' + block_height + ' from zcashd.')
        return False
    return json.loads(output)

def main():
    if not is_zcashd_running():
        sys.exit(1)

    args = parse_cmd_args()

    if (args.start and args.end):
        start_point = args.start
        end_point = args.end
    else:
        start_point = config.START_BLOCK_HEIGHT
        end_point = config.END_BLOCK_HEIGHT

    num_blocks = zcash('getinfo')['blocks'] if zcash('getinfo') is not False else None
    if num_blocks is not None:
        session = requests.session()
        session.headers.update({'Content-Type': 'application/json'})
        for x in range(start_point if (start_point > 0) else start_point,
            end_point if (end_point < num_blocks) else end_point):
                block = get_block(str(x))
                r = session.post(config.BLOCK_OBSERVATORY_URL, json=block)
                r.raise_for_status()
                print('Uploaded block ' + str(x) + '.')
    else:
        print('Error: Can\'t retrieve blocks from zcashd.')
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
