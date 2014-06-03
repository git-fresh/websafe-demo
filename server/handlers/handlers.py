import tornado.web
import os, sys, json
import requests

from urllib import urlencode
from httplib2 import Http

from settings import (
    GEOSERVER_REST_URL,
    GS_USERNAME,
    GS_PASSWORD,
    GEOSERVER_WORKSPACE,
    GEOSERVER_STORE,
    DATA_PATH,
    GEOSERVER_COOKIE_URL
)

from geoserver.catalog import Catalog


class IndexHandler(tornado.web.RequestHandler):
	def get(self):
            cookie = []
            cookie = self.get_cookie('JSESSIONID')
            try:
                if cookie is None:
                    headers = {'content-type': 'application/x-www-form-urlencoded'}
                    http = Http() 
                    data = dict(username=GS_USERNAME, password=GS_PASSWORD) 
                    resp = http.request(GEOSERVER_COOKIE_URL, method="POST", body=urlencode(data), headers=headers)

                    data_string = resp[0]['set-cookie']
                    cookie = data_string.split('=')
                    jsessionid = cookie[1].split(';')
                    self.set_cookie(cookie[0], jsessionid[0], path=cookie[2])
            except:
                pass

            self.render("index.html")

class WebsafeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("websafe.html")

class LayersHandler(tornado.web.RequestHandler):
    def get(self):
        temp_url = 'http://localhost:8080/geoserver/rest/layers.json'
        try:
            url = self.get_argument("api", temp_url)

            headers = {'Accept': '*/*'}
            resp = requests.get(url, auth=(GS_USERNAME,GS_PASSWORD), headers=headers)
        except:
            print 'Geoserver cannot be accessed.'
            pass
        else:
            self.write(resp.text)