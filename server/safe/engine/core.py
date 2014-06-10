"""Computational engine for InaSAFE core.

Provides the function calculate_impact()
"""

import numpy

from safe.storage.projection import Projection
from safe.storage.projection import DEFAULT_PROJECTION
from safe.impact_functions.core import extract_layers
from safe.common.utilities import unique_filename, verify
from utilities import REQUIRED_KEYWORDS
from safe.common.utilities import ugettext as tr


def calculate_impact(layers, impact_fcn, extent=None, check_integrity=True):
    """Calculate impact levels as a function of list of input layers

    Input
        layers: List of Raster and Vector layer objects to be used for analysis

        impact_fcn: Function of the form f(layers)

        extent:     List of [xmin, ymin, xmax, ymax]
                    the coordinates of the bounding box.

        check_integrity:    If true, perform checking of input data integrity

    Output
        filename of resulting impact layer (GML). Comment is embedded as
        metadata. Filename is generated from input data and date.

    Note
        The admissible file types are tif and asc/prj for raster and
        gml or shp for vector data

    Assumptions
        1. All layers are in WGS84 geographic coordinates
        2. Layers are equipped with metadata such as names and categories
    """

    # Input checks
    if check_integrity:
        check_data_integrity(layers)

    # Get an instance of the passed impact_fcn
    impact_function = impact_fcn()
    # Set extent if it is provided
    if not extent is None:
        impact_function.set_extent(extent)

    # Pass input layers to plugin
    F = impact_function.run(layers)

    # Get input layer sources
    # NOTE: We assume here that there is only one of each
    #       If there are more only the first one is used
    for cat in ['hazard', 'exposure']:
        L = extract_layers(layers, 'category', cat)
        keywords = L[0].get_keywords()
        not_specified = tr('Not specified')
        if 'title' in keywords:
            title = keywords['title']
        else:
            title = not_specified

        if 'source' in keywords:
            source = keywords['source']
        else:
            source = not_specified

        F.keywords['%s_title' % cat] = title
        F.keywords['%s_source' % cat] = source

    msg = 'Impact function %s returned None' % str(impact_function)
    verify(F is not None, msg)

    # Write result and return filename
    if F.is_raster:
        extension = '.tif'
        # use default style for raster
    else:
        extension = '.shp'
        # use default style for vector

    tempdir = "/vagrant/server/data/impact"
    output_filename2 = unique_filename(suffix=extension, dir=tempdir)

    #output_filename = unique_filename(suffix=extension)
    #output_filename = '/vagrant/backend/data/impact/impact.shp'
    #F.filename = output_filename2
    #F.write_to_file(output_filename2)

    # Establish default name (layer1 X layer1 x impact_function)
    if not F.get_name():
        default_name = ''
        for layer in layers:
            default_name += layer.name + ' X '

        if hasattr(impact_function, 'plugin_name'):
            default_name += impact_function.plugin_name
        else:
            # Strip trailing 'X'
            default_name = default_name[:-2]

        F.set_name(default_name)

    # FIXME (Ole): If we need to save style as defined by the impact_function
    #              this is the place

    # Return layer object
    return F


def check_data_integrity(layer_objects):
    """Check list of layer objects

    Input
        layer_objects: List of InaSAFE layer instances

    Output
        Nothing

    Raises
        Exceptions for a range of errors

    This function checks that
    * Layers have correct keywords
    * That they have the same georeferences
    """

    # Link to documentation
    manpage = ('http://risiko_dev.readthedocs.org/en/latest/usage/'
               'plugins/development.html')
    instructions = ('Please add keywords as <keyword>:<value> pairs '
                    ' in the .keywords file. For more information '
                    'please read the sections on impact functions '
                    'and keywords in the manual: %s' % manpage)

    # Set default values for projection and geotransform.
    # Enforce DEFAULT (WGS84).
    # Choosing 'None' will use value of first layer.
    reference_projection = Projection(DEFAULT_PROJECTION)
    geotransform = None

    for layer in layer_objects:

        # Check that critical keywords exist and are non empty
        keywords = layer.get_keywords()
        for kw in REQUIRED_KEYWORDS:
            msg = ('Layer %s did not have required keyword "%s". '
                   '%s' % (layer.name, kw, instructions))
            verify(kw in keywords, msg)

            val = keywords[kw]
            msg = ('No value found for keyword "%s" in layer %s. '
                   '%s' % (kw, layer.name, instructions))
            verify(val, msg)

        # Ensure that projection is consistent across all layers
        if reference_projection is None:
            reference_projection = layer.projection
        else:
            msg = ('Projections in input layer %s is not as expected:\n'
                   'projection: %s\n'
                   'default:    %s'
                   '' % (layer, layer.projection, reference_projection))
            verify(reference_projection == layer.projection, msg)

        tolerance = 10e-7

        # Ensure that geotransform and dimensions is consistent across
        # all *raster* layers
        if layer.is_raster:
            if geotransform is None:
                geotransform = layer.get_geotransform()
            else:
                msg = ('Geotransforms in input raster layers are different:\n'
                       '%s\n%s' % (geotransform, layer.get_geotransform()))
                verify(numpy.allclose(geotransform,
                                      layer.get_geotransform(),
                                      rtol=tolerance), msg)

        if layer.is_vector:
            msg = ('There are no vector data features. '
                   'Perhaps zoom out or pan to the study area '
                   'and try again')
            verify(len(layer) > 0, msg)

    # Check that arrays are aligned.

    refname = None
    for layer in layer_objects:
        if layer.is_raster:

            if refname is None:
                refname = layer.get_name()
                M = layer.rows
                N = layer.columns

            msg = ('Rasters are not aligned!\n'
                   'Raster %s has %i rows but raster %s has %i rows\n'
                   'Refer to issue #102' % (layer.get_name(),
                                            layer.rows,
                                            refname, M))
            verify(layer.rows == M, msg)

            msg = ('Rasters are not aligned!\n'
                   'Raster %s has %i columns but raster %s has %i columns\n'
                   'Refer to issue #102' % (layer.get_name(),
                                            layer.columns,
                                            refname, N))
            verify(layer.columns == N, msg)