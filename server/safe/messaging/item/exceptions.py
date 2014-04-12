"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Exceptions**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '11c37a0af8e588edd2ade7982aaadec63dfb0368'
__date__ = '11/06/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


class InvalidMessageItemError(Exception):
    """Custom exception for when the passed MessageElement is invalid."""
    pass
