import handlers

import json

import logging

import os

import tornado
import tornado.ioloop
import tornado.log
import tornado.options
import tornado.web

import typing

def get_cors_options() -> typing.Dict: 
    json_string = os.getenv('HMM_CORS', None)
    if not json_string:
        return None
    
    return json.loads(json_string)

def get_port() -> int:
    result = os.getenv('HMM_PORT', '8888')
    return int(result)

class HMMApplication(tornado.web.Application):

    cors_options: typing.Dict

    def __init__(self, handlers, cors_options: typing.Dict):
        self.cors_options = cors_options
        super().__init__(handlers)

if __name__ == '__main__':
    tornado.log.access_log.setLevel(logging.DEBUG)
    tornado.options.parse_command_line()

    base_dir = os.getenv('HMM_BASEDIR', os.path.dirname(os.path.realpath(__file__)))
    cors_options = get_cors_options()

    app = HMMApplication([
        (r'/.rest/pages', handlers.IndexHandler, dict(base_dir=base_dir)),
        (r'/.rest/pages/(.*)', handlers.MainHandler, dict(base_dir=base_dir)),
    ], cors_options)

    app.listen(get_port())
    tornado.ioloop.IOLoop.current().start()