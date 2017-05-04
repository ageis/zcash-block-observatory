#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
import ast, config, re, sqlite3, time

db_file = 'blocks.sqlite'
app = Flask(__name__)
app.config.from_object(config.FlaskConfig)

def latest_block():
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT MAX(height) FROM blocks')
    total_height = c.fetchone()
    return int(total_height[0])

def find_block_by_tx(txid):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT hash FROM tx WHERE tx=:txid', {"txid": txid})
    block_hash = c.fetchone()
    return str(block_hash['hash'])

def find_block_by_height(block_height):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT hash FROM blocks WHERE height=:height', {"height": block_height})
    block_hash = c.fetchone()
    return str(block_hash['hash'])

def get_single_block(block_hash):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM blocks WHERE hash=:hash', {"hash": block_hash})
    block = c.fetchone()
    transactions = ast.literal_eval(block['tx'])
    return dict(block), list(transactions)

def get_blocks():
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT hash, height, size, txs, time FROM blocks ORDER by height DESC LIMIT 200')
    # return retrieved blocks as a dict
    blocks = [dict(block) for block in c.fetchall()]
    return blocks

def validate_input(search_string):
    if search_string.isdigit():
        if int(search_string) <= latest_block():
            print('Search is numeric but not less than the current block height.')
            return search_string
    if len(search_string) != 64:
        print('Error: Search does not consist of 64 characters.')
        return None
    m = re.match(r"[A-Fa-f0-9]{64}", search_string)
    if m and m.span()[1] == len(search_string):
        print('Search matches hexademical format of a block hash or txid.')
        return search_string
    else:
        return None

@app.template_filter('timestamp')
def _jinja2_filter_timestamp(unix_epoch):
    return time.ctime(unix_epoch)

@app.route('/')
def index():
    try:
        blocks = get_blocks()
    except:
        pass
    return render_template('blocks.html', blocks = blocks)

@app.route('/block', methods = ['GET', 'POST'])
def show_block():
    print('Searching: ' + request.values.get('search'))
    search_string = validate_input(request.values.get('search').strip().lower())
    if search_string is None:
        print('Error: Search string was invalid.')
        return ('', 204)
    # find block by hash
    try:
        block, transactions = get_single_block(search_string)
        return render_template('block.html', block = block, transactions = transactions)
    except Exception as e:
        print(e)
        print('Error: Failed to locate block by hash.')
        pass
    # find block by transaction ID
    try:
        block_hash = find_block_by_tx(search_string)
        block, transactions = get_single_block(block_hash)
        return render_template('block.html', block = block, transactions = transactions)
    except Exception as e:
        print(e)
        print('Error: Failed to locate block by txid.')
        pass
    # find block by height
    try:
        block_hash = find_block_by_height(search_string)
        block, transactions = get_single_block(block_hash)
        return render_template('block.html', block = block, transactions = transactions)
    except Exception as e:
        print(e)
        print('Error: Failed to locate block by height.')
        return ('', 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int('8201'), debug=True)
