import tornado.web
import os, sys, json


from safe.api import read_layer, calculate_impact

# Flood Building Impact Function
from safe.impact_functions.inundation.flood_OSM_building_impact \
    import FloodBuildingImpactFunction

# Flood Population Evacuation Function
from safe.impact_functions.inundation.flood_population_evacuation_polygon_hazard \
    import FloodEvacuationFunctionVectorHazard


# Test Impact function
from safe.impact_functions.noah.flood_OSM_building_impact \
    import NOAHFloodBuildingImpactFunction

from settings import DATA_PATH, GS_IMPACT_WS

from utilities import make_data_dirs, upload_impact_vector, print_pdf, \
    set_style, make_style
from geoserver.catalog import Catalog


class CalculateHandler(tornado.web.RequestHandler):
    def get(self):
        data = dict()
        encoding = sys.getfilesystemencoding()
        exposure_name = ''

        hazard_name = "%s.shp" % self.get_argument("hazard_name")
        hazard_path = os.path.join(DATA_PATH, 'hazard', hazard_name)
        impact_function_keyword = self.get_argument("impact_function")

        if impact_function_keyword == 'structure':
            exposure_name = "%s.shp" % self.get_argument("exposure_name")
            #impact_function = FloodBuildingImpactFunction
            impact_function = NOAHFloodBuildingImpactFunction
        elif impact_function_keyword == 'population':
            exposure_name = "%s.tif" % self.get_argument("exposure_name")
            impact_function = FloodEvacuationFunctionVectorHazard

        exposure_path = os.path.join(DATA_PATH, 'exposure', exposure_name)

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

            haz_fnam, ext = os.path.splitext(hazard_name)
            exp_fnam, ext = os.path.splitext(exposure_name)
            impact_base_name = "IMPACT_%s_%s" % (exp_fnam, haz_fnam)
            impact_filename = impact_base_name + '.shp'
            impact_summary = "IMPACT_%s_%s.html" % (exp_fnam, haz_fnam)

            output = str(os.path.join(DATA_PATH, 'impact', impact_filename))
            output_summary = str(os.path.join(DATA_PATH, 'impact summary', impact_summary))

            if os.path.exists(output) and os.path.exists(output_summary):
                print 'impact file and impact summary already exists!'
                data = {
                    'return': 'success',
                    'resource': impact_base_name,
                }
                with open(output_summary) as html:
                    data['html'] = html.read()
                    print_pdf(data['html'], impact_base_name)
                    html.close()
            else:
                try:
                    impact = calculate_impact(
                        layers=[exposure_layer, hazard_layer],
                        impact_fcn=impact_function
                    )
                    impact.write_to_file(output)
                    data = upload_impact_vector(output)

                    #create the impact summary file
                    make_data_dirs()

                    result = impact.keywords["impact_summary"]
                    with open(output_summary, 'w+') as summary:
                        summary.write(result)
                        summary.close()

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
            report_path = os.path.join(DATA_PATH, 'impact report', impact_name)
            data = open(report_path)
            f = data.read()
            self.set_header("Content-Type", "application/pdf")
            self.write(f)
            data.close()
        except:
            raise