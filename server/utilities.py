import sys, requests, os

from paver.easy import path, sh, info, call_task

from geoserver.catalog import Catalog

from settings import GEOSERVER_REST_URL, GS_USERNAME, \
    GS_PASSWORD, GEOSERVER_WORKSPACE, GEOSERVER_STORE

def make_data_dirs():
	try:
		impact_dir = path('data/impact')
		if not impact_dir.exists():
			impact_dir.makedirs()

		impact_summary_dir = path('data/impact summary')
		if not impact_summary_dir.exists():
			impact_summary_dir.makedirs()
	except:
		raise

def print_pdf(html):
    html = self.get_argument("html")
    output = os.path.join(DATA_PATH, 'pdf', 'report.pdf')
    data = open(os.path.join(ROOT, 'static', 'css', 'pdf.css'))
    css = data.read()
    data.close()
    HTML(string=html).write_pdf(output, stylesheets=[CSS(string=css)])
    return

def upload_to_geoserver(impact_file_path):
    data = dict()
    try:
        cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
        ws = cat.get_workspace(GEOSERVER_WORKSPACE)
        ds = cat.get_store(GEOSERVER_STORE)

        base = str(os.path.splitext(impact_file_path)[0])
        name = str(os.path.splitext(os.path.basename(base))[0])

        shp = impact_file_path
        shx = base + '.shx'
        dbf = base + '.dbf'
        prj = base + '.prj'
        data = { 
                 'shp' : shp,
                 'shx' : shx,
                 'dbf' : dbf,
                 'prj' : prj
               }
        cat.add_data_to_store(ds, name, data, ws, True)
        set_style(name, "Flood Impact")
        layer = { 
                    'workspace': GEOSERVER_WORKSPACE,
                    'store'    : GEOSERVER_STORE,
                    'resource' : name
                }
        data = {'return':'ok', 'layer': layer }
    except:
        raise
    else:
        return data

def set_style(layer_name, style):
    cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
    layer = cat.get_layer(layer_name)

    if style is None:
        print 'No style specified!'
        return
    
    style = cat.get_style(style, GEOSERVER_WORKSPACE)
    layer.default_style = style
    cat.save(layer)
