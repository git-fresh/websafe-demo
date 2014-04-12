from handlers.handlers import IndexHandler, WebsafeHandler, LayersHandler, \
	CalculateHandler

import os.path
import tornado.web

# This is where we encode the urls with their respective handlers   
handlers = [
    (r"/", IndexHandler)
]

#This adds the modules that AngularJS' routing service uses
handlers += [
    (r"/api/websafe", WebsafeHandler),
    (r"/api/layers", LayersHandler),
    (r"/api/calculate", CalculateHandler),
]

class Application(tornado.web.Application):
	def __init__(self):
		settings = dict(
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			debug=True,
		)
		tornado.web.Application.__init__(self, handlers, **settings)