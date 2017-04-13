#!/usr/bin/python3
# -*- coding: utf-8 -*-

from functools import wraps
from flask import Flask, g, abort, jsonify, render_template, request, Response, session
import config, json, os, re, sqlite3, sys, time
from werkzeug.contrib.cache import SimpleCache

db_file = 'blocks.sqlite'
app = Flask(__name__)
app.config.from_object(config.FlaskConfig)

def find_block(txid):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT hash FROM tx WHERE tx=:txid', {"txid": txid})
    block_hash = c.fetchone()
    return str(block_hash['hash'])

def get_blocks(block_hash=None):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if block_hash is not None:
        c.execute('SELECT * FROM blocks WHERE hash=:hash LIMIT 20', {"hash": block_hash})
        block = dict(c.fetchone())
        txs = get_txs(block['hash'])
        block['tx'] = txs
        return block
    else:
        c.execute('SELECT hash, height, size, time FROM blocks ORDER by height DESC LIMIT 20')
        blocks = [dict(block) for block in c.fetchall()]
        for block in blocks:
            txs = get_txs(block['hash'])
            block['tx'] = txs
        return blocks

def get_txs(block_hash):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT tx FROM tx WHERE hash=:hash', {"hash": block_hash})
    txs = [dict(tx) for tx in c.fetchall()]
    return txs

def validate_input(search_string):
    if len(search_string) != 64:
        return None
    m = re.match(r"[A-Fa-f0-9]{64}", search_string)
    if m and m.span()[1] == len(search_string):
        return search_string
    else:
        return None

@app.template_filter('timestamp')
def _jinja2_filter_timestamp(unix_epoch):
    return time.ctime(unix_epoch)

@app.route('/')
def index():
    blocks = cache.get('blocks')
    return render_template('blocks.html', blocks = blocks)

@app.route('/block', methods = ['GET', 'POST'])
def show_block():
    search_string = validate_input(request.values.get('search').strip().lower())
    if search_string is None:
        return ('', 204)
    try:
        block = get_blocks(search_string)
        return render_template('block.html', block = block)
    except:
        pass
    try:
        block_hash = find_block(search_string)
        block = get_blocks(block_hash)
        return render_template('block.html', block = block)
    except:
        return ('', 204)

if __name__ == '__main__':
    cache = SimpleCache()
    cache.set('blocks', get_blocks(), timeout=3600)
    app.run(host='0.0.0.0', port=int('8201'), debug=True)
