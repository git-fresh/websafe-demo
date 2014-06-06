import sys, requests, os, math

from geoserver.catalog import Catalog

from settings import (
    GEOSERVER_REST_URL,
    GS_USERNAME,
    GS_PASSWORD,
    GS_EXPOSURE_WS,
    GS_HAZARD_WS,
    GS_IMPACT_WS,
    DATA_PATH,
    ROOT
)

from sld import *

from weasyprint import HTML, CSS

def make_data_dirs():
    try:
        impact_report_dir = os.path.join(DATA_PATH, 'impact report')
        if not os.path.exists(impact_report_dir):
            os.makedirs(impact_report_dir)

        impact_summary_dir = os.path.join(DATA_PATH, 'impact summary')
        if not os.path.exists(impact_summary_dir):
            os.makedirs(impact_summary_dir)
    except:
        raise

# TODO: to be removed if jsPDF report generation is a success
def print_pdf(html, impact_name):
    try:
        impact_report_filename = "%s.pdf" % impact_name

        output = os.path.join(DATA_PATH, 'impact report', impact_report_filename)
        data = open(os.path.join(ROOT, 'static', 'css', 'pdf.css'))
        css = data.read()
        HTML(string=html).write_pdf(output, stylesheets=[CSS(string=css)])
        data.close()
    except:
        raise

def upload_impact_vector(impact_file_path):
    data = dict()
    try:
        cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
        ws = cat.get_workspace(GS_IMPACT_WS)

        base = str(os.path.splitext(impact_file_path)[0])
        name = str(os.path.splitext(os.path.basename(base))[0])

        shx = base + '.shx'
        dbf = base + '.dbf'
        prj = base + '.prj'
        data = { 
                 'shp' : impact_file_path,
                 'shx' : shx,
                 'dbf' : dbf,
                 'prj' : prj
               }

        cat.create_featurestore(name, data, ws, True)

        data = {'return': 'success', 'resource' : name }
    except:
        return {'return': 'fail'}
    else:
        return data

def upload_raster(impact_file_path):
    data = dict()
    try:
        cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
        ws = cat.get_workspace(GS_IMPACT_WS)

        base = str(os.path.splitext(impact_file_path)[0])
        name = str(os.path.splitext(os.path.basename(base))[0])

        cat.create_coveragestore(name, impact_file_path, ws, True)
    except:
        raise

""" Set the style of the layer with name: layer_name
"""
def set_style(layer_name, style):
    try:
        cat = Catalog(GEOSERVER_REST_URL, GS_USERNAME, GS_PASSWORD)
        layer = cat.get_layer(layer_name)
    
        style = cat.get_style(style)
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
        cat.create_style(style_name, style.read(), overwrite=True)
        style.close()
    