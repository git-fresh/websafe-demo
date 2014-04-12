from urls import Application

import tornado.httpserver
import tornado.ioloop
import tornado.options
import os

def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(os.environ.get("PORT", 5000))
        print "Server running on port:", os.environ.get("PORT", 5000)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()