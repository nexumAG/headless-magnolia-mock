import json

import logging

import os
import os.path

import tornado
import tornado.ioloop
import tornado.log
import tornado.options
import tornado.web

import typing

class BaseHandler(tornado.web.RequestHandler):

    cors_options: typing.Dict

    base_dir: typing.AnyStr

    def initialize(self, base_dir: typing.AnyStr):
        self.base_dir = base_dir

    def set_default_headers(self):
        cors_options = self.application.cors_options
        if not cors_options:
            return
        
        for header_name in cors_options:
            self.set_header(header_name, cors_options[header_name])

    def get_response_object(self, request_path: typing.AnyStr) -> typing.Dict:
        file_path = request_path
        if not request_path:
            file_path = '_index.json'

        result = os.path.join(self.base_dir, file_path)
        if not result.endswith('.json'):
            result += '.json'
        
        if not os.path.exists(result):
            return None

        with open(result, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)

    def options(self):
        # support for CORS
        self.set_status(204)
        self.finish()

class IndexHandler(BaseHandler):
    async def get(self):
        response_object = self.get_response_object('_index')
        if not response_object:
            self.set_status(404)
            return

        self.write(response_object)
        self.set_status(response_object['status'])

class MainHandler(BaseHandler):

    async def get(self, path: typing.AnyStr):
        response_object = self.get_response_object(path)
        if not response_object:
            self.set_status(404)
            return

        self.write(response_object)
        self.set_status(response_object['status'])

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
        (r'/.rest/pages', IndexHandler, dict(base_dir=base_dir)),
        (r'/.rest/pages/(.*)', MainHandler, dict(base_dir=base_dir)),
    ], cors_options)

    app.listen(get_port())
    tornado.ioloop.IOLoop.current().start()