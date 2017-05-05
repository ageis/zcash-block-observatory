#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Sends incoming blocks from a locally-running zcashd to a remote collector.
"""
import json
import time
import subprocess
import sys
import requests

from config import SendBlocksConfig
config = SendBlocksConfig

def zcash(block_hash):
    zcexec = subprocess.Popen([config.ZCASH_CLI_PATH, 'getblock', block_hash], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = zcexec.communicate()[0]
    return json.loads(output)

def main():
    timestamp = int(time.time())
    block_hash = str(sys.argv[1])
    block = zcash(block_hash)
    block['arrivaltime'] = timestamp
    session = requests.session()
    session.headers.update({'Content-Type': 'application/json'})
    r = session.post(config['BLOCK_OBSERVATORY_URL'], json=block)
    r.raise_for_status()
    sys.exit(0)

if __name__ == '__main__':
    main()
