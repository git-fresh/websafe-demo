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

class ExposureHandler(tornado.web.RequestHandler):
    def get(self):
        to_return = []
        vector_url = 'http://localhost:8080/geoserver/rest/workspaces/exposure/datastores.json'
        raster_url = 'http://localhost:8080/geoserver/rest/workspaces/exposure/coveragestores.json'

        try:
            vector = requests.get(vector_url, auth=(GS_USERNAME,GS_PASSWORD))
            vector_json = json.loads(vector.text)
            raster = requests.get(raster_url, auth=(GS_USERNAME,GS_PASSWORD))
            raster_json = json.loads(raster.text)

            if vector_json['dataStores'] != "":
                to_return.extend(vector_json['dataStores']['dataStore'])

            if raster_json['coverageStores'] != "":
                to_return.extend(raster_json['coverageStores']['coverageStore'])

        except:
            raise
        else:
            self.write(json.dumps(to_return))

class HazardHandler(tornado.web.RequestHandler):
    def get(self):
        to_return = []
        vector_url = 'http://localhost:8080/geoserver/rest/workspaces/hazard/datastores.json'
        raster_url = 'http://localhost:8080/geoserver/rest/workspaces/hazard/coveragestores.json'

        try:
            vector = requests.get(vector_url, auth=(GS_USERNAME,GS_PASSWORD))
            vector_json = json.loads(vector.text)
            raster = requests.get(raster_url, auth=(GS_USERNAME,GS_PASSWORD))
            raster_json = json.loads(raster.text)

            if vector_json['dataStores'] != "":
                to_return.extend(vector_json['dataStores']['dataStore'])

            if raster_json['coverageStores'] != "":
                to_return.extend(raster_json['coverageStores']['coverageStore'])

        except:
            raise
        else:
            self.write(json.dumps(to_return))

class GetCapabilitiesHandler(tornado.web.RequestHandler):
    def get(self):
        url = 'http://localhost:8080/geoserver/ows?service=wms&version=1.1.1&request=GetCapabilities'
        try:
            resp = requests.get(url, auth=(GS_USERNAME,GS_PASSWORD))
            self.set_header("Content-Type", "application/xml")
            self.write(resp.text)
        except:
            raise