#!/usr/bin/python
# -*- coding: utf-8 -*-

import json, os, requests, subprocess, sys, time
block_observatory_url = 'http://127.0.0.1:8200/'

def zcash(cmd):
    zcash = subprocess.Popen(['/usr/bin/zcash-cli', cmd], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = zcash.communicate()[0]
    return json.loads(output)

def get_block(block_height):
    zcash = subprocess.Popen(['/usr/bin/zcash-cli', 'getblock', block_height], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = zcash.communicate()[0]
    return json.loads(output)

def main():
    number_of_blocks = zcash('getinfo')['blocks']
    session = requests.session()
    session.headers.update({'Content-Type': 'application/json'})
    for x in range (0, number_of_blocks):
        block = get_block(str(x))
        r = session.post(block_observatory_url, json=block)
        r.raise_for_status()

if __name__ == '__main__':
    main()
