import tornado.web
import os, sys, json
import requests


from safe.api import read_layer, calculate_impact
from safe.impact_functions.core import requirements_collect, get_doc_string, \
    requirement_check
from safe.impact_functions.inundation.flood_OSM_building_impact \
    import FloodBuildingImpactFunction

from settings import (
    GEOSERVER_REST_URL,
    GS_USERNAME,
    GS_PASSWORD,
    GEOSERVER_WORKSPACE,
    GEOSERVER_STORE,
    DATA_PATH
)

from utilities import make_data_dirs, upload_to_geoserver, print_pdf
from geoserver.catalog import Catalog


class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("index.html")       

class WebsafeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("websafe.html")

class LayersHandler(tornado.web.RequestHandler):
    def get(self):
        temp_url = 'http://localhost:8080/geoserver/rest/layers.json'
        cat = Catalog("http://localhost:8080/geoserver/rest",
            username=GS_USERNAME, password=GS_PASSWORD)
        all_layers = cat.get_layers()
        
        url = self.get_argument("api", temp_url)

        headers = {'Accept': '*/*'}
        resp = requests.get(url, auth=(GS_USERNAME,GS_PASSWORD), headers=headers)
        self.write(resp.text)
        
class CalculateHandler(tornado.web.RequestHandler):
    def get(self):
        data = dict()
        extension = '.shp'
        encoding = sys.getfilesystemencoding()
        hazard_title = self.get_argument("hazard_title") + extension
        hazard_path = os.path.join(DATA_PATH, 'hazard', hazard_title)

        exposure_title = self.get_argument("exposure_title") + extension
        exposure_path = os.path.join(DATA_PATH, 'exposure', exposure_title)

        try:
            hazard_layer = read_layer(hazard_path.encode(encoding))
            exposure_layer = read_layer(exposure_path.encode(encoding))

            # assign the required keywords for inasafe calculations
            exposure_layer.keywords['category'] = 'exposure'
            hazard_layer.keywords['category'] = 'hazard'
            exposure_layer.keywords['subcategory'] = self.get_argument("exposure_subcategory")
            hazard_layer.keywords['subcategory'] = self.get_argument("hazard_subcategory")
                
            #define a method that determines the correct impact function based on keywords given
            impact_function = FloodBuildingImpactFunction
            #requirements = requirements_collect(impact_function)
            #print requirements
            #requirement_check(params=params, require_str=requirements, verbose=True)

            haz_fnam, ext = os.path.splitext(hazard_title)
            exp_fnam, ext = os.path.splitext(exposure_title)
            impact_base_name = "IMPACT_%s_%s" % (exp_fnam, haz_fnam)
            impact_filename = impact_base_name + '.shp'
            impact_summary = "IMPACT_%s_%s.html" % (exp_fnam, haz_fnam)

            output = str(os.path.join(DATA_PATH, 'impact', impact_filename))
            output_summary = str(os.path.join(DATA_PATH, 'impact summary', impact_summary))

            if os.path.exists(output) and os.path.exists(output_summary):
                print 'impact file and impact summary already exists!'
                html = open(output_summary)
                f = html.read()
                layer = { 
                        'workspace': GEOSERVER_WORKSPACE,
                        'store'    : GEOSERVER_STORE,
                        'resource' : impact_base_name
                    }
                data = {'return':'ok', 'layer': layer, 'html' : f}
            else:
                try:
                    make_data_dirs()

                    impact = calculate_impact(
                        layers=[exposure_layer, hazard_layer],
                        impact_fcn=impact_function
                    )
                    impact.write_to_file(output)

                    #create the impact summary file
                    result = impact.keywords["impact_summary"]
                    with open(output_summary, 'w') as summary:
                        summary.write(result)
                        summary.close()

                    data = upload_to_geoserver(output)
                    data['html'] = result
                    print_pdf(result, impact_base_name)
                except:
                    raise
        except:
                print 'IO Error or something else has occurred!'
                raise
        else:
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(data))

class ImpactPdfHandler(tornado.web.RequestHandler):
    def get(self):
        impact_name = "%s.pdf" % self.get_argument("q")
        try:
            data = open(os.path.join(DATA_PATH, 'impact report', impact_name))
            f = data.read()
            self.set_header("Content-Type", "application/pdf")
            self.write(f)
            data.close()
        except:
            raise
