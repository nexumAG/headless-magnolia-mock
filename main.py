import json

import logging

import os
import os.path

import tornado
import tornado.ioloop
import tornado.log
import tornado.web

import typing

class BaseHandler(tornado.web.RequestHandler):

    base_dir: typing.AnyStr

    def initialize(self, base_dir: typing.AnyStr):
        self.base_dir = base_dir

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



def get_port() -> int:
    result = os.getenv('HMM_PORT', '8888')
    return int(result)

if __name__ == '__main__':
    tornado.log.access_log.setLevel(logging.DEBUG)

    app = tornado.web.Application([
        (r'/.rest/pages', IndexHandler, dict(base_dir=os.getenv('HMM_BASEDIR', os.path.dirname(os.path.realpath(__file__))))),
        (r'/.rest/pages/(.*)', MainHandler, dict(base_dir=os.getenv('HMM_BASEDIR', os.path.dirname(os.path.realpath(__file__))))),
    ])

    app.listen(get_port())
    tornado.ioloop.IOLoop.current().start()