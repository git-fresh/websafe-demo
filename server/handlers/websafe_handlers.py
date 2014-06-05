import tornado.web
import os, sys, json
import requests


from safe.api import read_layer, calculate_impact

# Flood Building Impact Function
from safe.impact_functions.inundation.flood_OSM_building_impact \
    import FloodBuildingImpactFunction

# Flood Population Evacuation Function
from safe.impact_functions.inundation.flood_population_evacuation_polygon_hazard \
    import FloodEvacuationFunctionVectorHazard

from settings import (
    GEOSERVER_REST_URL,
    GS_USERNAME,
    GS_PASSWORD,
    GEOSERVER_WORKSPACE,
    GEOSERVER_STORE,
    DATA_PATH,
    GEOSERVER_COOKIE_URL
)

from utilities import make_data_dirs, upload_to_geoserver, print_pdf, \
    set_style, make_style
from geoserver.catalog import Catalog


class CalculateHandler(tornado.web.RequestHandler):
    def get(self):
        data = dict()
        encoding = sys.getfilesystemencoding()
        exposure_title = ''

        hazard_title = "%s.shp" % self.get_argument("hazard_title")
        hazard_path = os.path.join(DATA_PATH, 'hazard', hazard_title)
        impact_function_keyword = self.get_argument("impact_function")

        if impact_function_keyword == 'structure':
            exposure_title = "%s.shp" % self.get_argument("exposure_title")
            impact_function = FloodBuildingImpactFunction
        elif impact_function_keyword == 'population':
            exposure_title = "%s.tif" % self.get_argument("exposure_title")
            impact_function = FloodEvacuationFunctionVectorHazard

        exposure_path = os.path.join(DATA_PATH, 'exposure', exposure_title)

        try:
            hazard_layer = read_layer(hazard_path.encode(encoding))
            exposure_layer = read_layer(exposure_path.encode(encoding))

            # hardcoded the required keywords for inasafe calculations
            exposure_layer.keywords['category'] = 'exposure'
            hazard_layer.keywords['category'] = 'hazard'
            hazard_layer.keywords['subcategory'] = 'flood'

            if impact_function_keyword == 'structure':
                exposure_layer.keywords['subcategory'] = 'structure'
            elif impact_function_keyword == 'population':
                exposure_layer.keywords['subcategory'] = 'population'

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
                print_pdf(html, impact_base_name)
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

                    if impact_function_keyword == 'population':
                        make_style(impact_base_name, impact.style_info)
                        set_style(impact_base_name, impact_base_name)
                    else:
                        set_style(impact_base_name, "Flood-Building")

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