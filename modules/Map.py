#!/usr/bin/env python

import ee, folium

ee.Initialize()
# class Map():

def addLayer(eeObject, visParams={}, name='layer'):
    """Function to view Google Earth Engine tile layer as a Folium map.
    
    Parameters
        m (object): Folium map
        eeObject (ee.Object): Earth Engine Object.
        visParams (dict): Dictionary with visualization parameters.
        name (str): Layer name.
    
    Returns:
    """
        
    mapid = ee.Image(eeObject).getMapId(visParams)

    url = "https://earthengine.googleapis.com/v1/{mapid}/tiles/{{z}}/{{x}}/{{y}}"

    tiles = url.format(mapid=mapid['mapid'])

    m = folium.Map(zoom_start=12, tiles='Cartodb dark_matter')

    # rgb layer
    folium.raster_layers.TileLayer(
        tiles = tiles,
        attr = 'Google Earth Engine',
        name = name,
        max_zoom = 20,
        subdomains = ['mt0', 'mt1', 'mt2', 'mt3'],
        overlay = True,
        control = True,
    ).add_to(m)

    return m