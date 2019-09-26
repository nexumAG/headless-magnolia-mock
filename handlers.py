import json

import os
import os.path

import tornado
import tornado.gen
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
        if os.path.isdir(result):
            result = os.path.join(result, '_index.json')
        elif not result.endswith('.json'):
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
