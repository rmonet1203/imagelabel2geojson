# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ImageLabel2GeoJSON
                                 A QGIS plugin
 ImageLabel to GeoJSON
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-07-09
        copyright            : (C) 2023 by GeoMaster
        email                : rmonet1203@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ImageLabel2GeoJSON class from file ImageLabel2GeoJSON.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ImageLabel2GeoJSON import ImageLabel2GeoJSON
    return ImageLabel2GeoJSON(iface)
