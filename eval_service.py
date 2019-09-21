import logging
import sys
import json
from tornado.web import RequestHandler, StaticFileHandler, Application
from tornado.options import define, options, parse_command_line
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from motor.motor_tornado import MotorClient
from log import logger

# 用于加密Cookie和AppKey/AppId
define('port', default='8080')
define('mongodb_url', default='mongodb://mongo-0.mongo,mongo-1.mongo,mongo-2.mongo/?replicaSet=rs0')
define('mongodb_db', default='audio_eval')


class EvalHandler(RequestHandler):
    async def put(self, tid=None):
        """
        params:
            exp
            reason
        """
        ip = self.request.headers['X-Forwarded-For'] if 'X-Forwarded-For' in self.request.headers else '0000'
        
        try: 
            data = json.loads(self.request.body.decode())
        except Exception as ex:
            logger.warn('{!r}'.format(ex))
            self.send_error(400, reason='Invalid json format')
            return

        logger.info(f'Request: {data}')

        if tid is None:
            self.send_error(400, reason='Need tid')
            return

        # if 'exp' not in data or 'reason' not in data:
        #     self.send_error(400, 'Missing key field')
        #     return

        db = self.settings['db']

        await db.test_results[tid].insert_one(data)
        self.finish()
    
    async def get(self, tid=None):
        if tid is None:
            logger.warn('Need a test id')
            self.send_error(500, reason='Need a test id')
            return

        self.render('index.html')
        

def ConfigHandler(RequestHandler):
    async def get(self, tid=None):
        if tid is None:
            logger.warn('Must has a specific id')
            self.send_error(400, reason='Must has a specific id')
            return
        
        db = self.settings['db']
        testsuite = db.testsuites[tid]
        self.render('config/abx_config_template.js',
            testsuite_name=testsuite.name,
            tests=testsuite.tests
        )


def main():

    app = Application([
        (r'/eval/(?P<tid>[\w/]+)', EvalHandler),
        (r'/eval/(?P<tid>[\w/]+)/submit', EvalHandler),
        (r'/eval/(?P<tid>[\w/]+)/config.js', ConfigHandler),
        (r"/img/(.*)",StaticFileHandler, {"path": "./img"}),
        (r"/css/(.*)",StaticFileHandler, {"path": "./css"}),
        (r"/js/(.*)",StaticFileHandler, {"path": "./js"}),
        ],
        template_path='static')


    server = HTTPServer(app)
    server.bind(options.port)
    server.start(1)

    app.settings['db'] = MotorClient(options.mongodb_url)[options.mongodb_db]

    try:
        IOLoop.current().asyncio_loop.run_until_complete(app.create_redis())
    except Exception as e:
        logger.error(f'Cannot connect to redis {e}')
        sys.exit(-1)
    
    IOLoop.current().start()
