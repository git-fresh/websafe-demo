from handlers.handlers import IndexHandler, WebsafeHandler, LayersHandler
from handlers.websafe_handlers import CalculateHandler, ImpactPdfHandler

import os.path
import tornado.web

# This is where we encode the urls with their respective handlers   
handlers = [
    (r"/", IndexHandler)
]

# api handlers
handlers += [
    (r"/api/websafe", WebsafeHandler),
    (r"/api/layers", LayersHandler),
    (r"/api/calculate", CalculateHandler),
    (r"/api/pdf", ImpactPdfHandler)
]

class Application(tornado.web.Application):
	def __init__(self):
		settings = dict(
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			debug=True,
		)
		tornado.web.Application.__init__(self, handlers, **settings)