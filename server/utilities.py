import sys, requests, os, math

from paver.easy import path, sh, info, call_task

from geoserver.catalog import Catalog

from settings import (
    GEOSERVER_REST_URL,
    GS_USERNAME,
    GS_PASSWORD,
    GEOSERVER_WORKSPACE,
    GEOSERVER_STORE,
    DATA_PATH,
    ROOT
)

from sld import *

from weasyprint import HTML, CSS


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

def print_pdf(html, impact_name):
    try:
        impact_report_dir = path('data/impact report')
        if not impact_report_dir.exists():
            impact_report_dir.makedirs()

        impact_report_filename = "%s.pdf" % impact_name

        output = os.path.join(DATA_PATH, 'impact report', impact_report_filename)
        data = open(os.path.join(ROOT, 'static', 'css', 'pdf.css'))
        css = data.read()
        HTML(string=html).write_pdf(output, stylesheets=[CSS(string=css)])
        data.close()
    except:
        raise

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

""" Set the style of the layer with name: layer_name
"""
def set_style(layer_name, style):
    try:
        cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
        layer = cat.get_layer(layer_name)

        if style is None:
            print 'No style specified!'
            return
    
        style = cat.get_style(style, GEOSERVER_WORKSPACE)
        layer.default_style = style
        cat.save(layer)
    except:
        raise

""" Make SLD styles based on style_info(dict of style classes)
    and upload on Geoserver. 
"""
def make_style(style_name, style_info):
    cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
    style_dir = path('data/styles')
    if not style_dir.exists():
        style_dir.makedirs()

    style_filename = style_name + '.sld'
    style_file_path = str(os.path.join(DATA_PATH, 'styles', style_filename))

    target_field = style_info['target_field']

    sld_doc = StyledLayerDescriptor()
    nl = sld_doc.create_namedlayer(style_name)
    us = nl.create_userstyle()
    feature_style = us.create_featuretypestyle()

    for x in style_info['style_classes']:
        elem = feature_style._node.makeelement('{%s}Rule' % SLDNode._nsmap['sld'], nsmap=SLDNode._nsmap)
        feature_style._node.append(elem)

        r = Rule(feature_style, len(feature_style._node)-1)
        r.Title = x['label']

        f1 = Filter(r)
        f1.PropertyIsGreaterThanOrEqualTo = PropertyCriterion(f1, 'PropertyIsGreaterThanOrEqualTo')
        f1.PropertyIsGreaterThanOrEqualTo.PropertyName = target_field
        f1.PropertyIsGreaterThanOrEqualTo.Literal = str(round(x['min']))

        f2 = Filter(r)
        f2.PropertyIsLessThan = PropertyCriterion(f2, 'PropertyIsLessThan')
        f2.PropertyIsLessThan.PropertyName = target_field
        f2.PropertyIsLessThan.Literal = str(round(x['max']))

        r.Filter = f1 + f2

        sym = PolygonSymbolizer(r)
        fill = Fill(sym)
        fill.create_cssparameter('fill', x['colour'])
        fill.create_cssparameter('fill-opacity', '0.5')

    with open(style_file_path, 'w') as style:
        style.write(sld_doc.as_sld(True))
        style.close()

    with open(style_file_path, 'r') as style:
        cat.create_style(style_name, style.read(), workspace=GEOSERVER_WORKSPACE, overwrite=True)
        style.close()
    