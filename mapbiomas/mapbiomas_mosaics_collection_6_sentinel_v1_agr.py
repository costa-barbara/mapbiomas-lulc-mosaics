#
import sys, os

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('../gee_toolbox'))

import gee as gee_toolbox
import json

# Import modules
from modules.CloudAndShadowMask import *
from modules.SpectralIndexes import *
from modules.Miscellaneous import *
from modules.SmaAndNdfi import *
from modules.Collection import *
from modules.BandNames import *
from modules.DataType import *
from modules.Mosaic import *

# Set up version
version = 1

gridsAsset = 'projects/mapbiomas-workspace/AUXILIAR/cartas'
collectionId = 'projects/nexgenmap/MapBiomas2/SENTINEL/mosaics-agr'

# ancillary data
jsonFile = '../data.json'

# nome do bioma sem espaço
BIOME_NAME = 'PANTANAL'

year = 2020

dateStart = str(year-1) + '-10-01'
dateEnd = str(year) + '-04-30'

MAX_CLOUD_PROBABILITY = 40
MAX_CLOUD_COVER = 80

ACCOUNT = 'mapbiomas1'

jsonData = json.load(open(jsonFile, 'r'))

gridNames = jsonData['grids'][BIOME_NAME][:1]

grids = ee.FeatureCollection(gridsAsset)\
    .filter(
        ee.Filter.inList('grid_name', gridNames)
    )

collectionIds = {
    'sentinel2': 'COPERNICUS/S2_SR',
}

bufferSize = 100

S2_CLOUD_PROBABILITY = 'COPERNICUS/S2_CLOUD_PROBABILITY'

def applyCloudMask(collection, maxCloudProbability=40):

    criteria = ee.Filter.date(dateStart, dateEnd)

    cloudProbability = ee.ImageCollection(S2_CLOUD_PROBABILITY)\
        .filter(criteria)

    collectionWithCloudMask = ee.Join.saveFirst('cloud_mask')\
        .apply(
            primary=collection,
            secondary=cloudProbability,
            condition=ee.Filter.equals(
                leftField='system:index',
                rightField='system:index'
            )
    )

    def cloudMasking(image):

        clouds = ee.Image(image.get('cloud_mask')).select('probability')

        isNotCloud = clouds.lt(maxCloudProbability)

        return image.updateMask(isNotCloud)

    collectionWithoutClouds = ee.ImageCollection(collectionWithCloudMask)\
        .map(cloudMasking)

    return collectionWithoutClouds


for gridName in gridNames:

    gee_toolbox.switch_user(ACCOUNT)
    gee_toolbox.init()

    try:

        # define a geometry
        grid = grids.filter(ee.Filter.stringContains(
            'grid_name', gridName))
            
        grid = ee.Feature(grid.first()).geometry()\
            .buffer(bufferSize).bounds()

        # returns a collection containing the specified parameters
        collection = getCollection(collectionIds['sentinel2'],
                                   dateStart=dateStart,
                                   dateEnd=dateEnd,
                                   cloudCover=MAX_CLOUD_COVER,
                                   geometry=grid
                                   )

        # returns a pattern of band names
        bands = getBandNames('sentinel2')

        # Rename collection image bands
        collection = collection.select(
            bands['bandNames'],
            bands['newNames']
        )
        
        collection = applyCloudMask(collection, maxCloudProbability=MAX_CLOUD_PROBABILITY)

        # calculate Spectral indexes
        collection = collection\
            .map(getEVI2)\
            .map(getNDWI)
        
        # generate mosaic       
        mosaic = getMosaic(collection,
                           percentileDry=20,
                           percentileWet=75,
                           percentileBand='evi2',
                           dateStart=dateStart,
                           dateEnd=dateEnd)

        print(mosaic.bandNames().getInfo())

        mosaic = setBandTypes(mosaic, mtype="agriculture")
        
        # print(mosaic.bandNames().getInfo())

        mosaic = mosaic.set('year', year)
        mosaic = mosaic.set('collection', 6.0)
        mosaic = mosaic.set('grid_name', gridName)
        mosaic = mosaic.set('version', str(version))

        imageName = BIOME_NAME + '-' + \
            gridName + '-' + \
            str(year) + '-' + \
            str(version)
                
        print(imageName)

        task = ee.batch.Export.image.toAsset(
           image=mosaic,
           description=imageName,
           assetId=collectionId + '/' + imageName,
           region=grid.coordinates().getInfo(),
           scale=10,
           maxPixels=int(1e13)
        )
        
        # task.start()

    except Exception as e:
        print(e)
    
    ee.Reset()

gee_toolbox.switch_user('joao')
gee_toolbox.init()
