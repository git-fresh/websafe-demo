from handlers.handlers import IndexHandler, WebsafeHandler, \
    ExposureHandler, HazardHandler, GetCapabilitiesHandler
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
    (r"/api/calculate", CalculateHandler),
    (r"/api/pdf", ImpactPdfHandler),
    (r"/exposures", ExposureHandler),
    (r"/hazards", HazardHandler),
    (r"/getcapabilities", GetCapabilitiesHandler)
]

class Application(tornado.web.Application):
	def __init__(self):
		settings = dict(
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			debug=True,
		)
		tornado.web.Application.__init__(self, handlers, **settings)