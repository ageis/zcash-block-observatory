#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This is a configuration file for the Zcash block observatory.
"""

class ShowBlocksConfig(object):
    BIND_PORT = 8201
    DB_FILE = 'blocks.sqlite'
    DEBUG = True
    TESTING = True
    TEMPLATE_DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = 'lQT0EE/XcyZrXDjCCJ/KRs3F2zKc0Ls3KAmT4y0pxp4='

class ReceiveBlocksConfig(object):
    BIND_PORT = 8200
    DB_FILE = 'blocks.sqlite'
    DEBUG = True
    TESTING = True

class SendBlocksConfig(dict):
    BLOCK_OBSERVATORY_URL = 'http://127.0.0.1:8200/'
    ZCASH_CLI_PATH = '/usr/bin/zcash-cli'

class LoadBlocksConfig(dict):
    BLOCK_OBSERVATORY_URL = 'http://127.0.0.1:8200/'
    ZCASH_CLI_PATH = '/usr/bin/zcash-cli'
    START_BLOCK_HEIGHT = 0
    END_BLOCK_HEIGHT = 108560

class ZcashConfig(dict):
    ZCASH_CLI_PATH = '/usr/bin/zcash-cli'
