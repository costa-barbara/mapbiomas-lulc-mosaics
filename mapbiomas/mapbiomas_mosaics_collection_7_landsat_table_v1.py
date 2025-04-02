#
import ee
import sys
import os

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath('../'))

from modules.CloudAndShadowMaskC2 import *
from modules.SpectralIndexes import *
from modules.Miscellaneous import *
from modules.SmaAndNdfi import *
from modules.Collection import *
from modules.BandNames import *
from modules.DataType import *
from modules.Mosaic import *

sys.path.append(os.path.abspath('../gee_toolbox'))
import gee as gee_toolbox

import pandas as pd
from datetime import datetime
from pprint import pprint

ee.Initialize()

# Set up account to use
ACCOUNT = 'joao'

version = '1'

versionMasks = '2'

gridsAsset = 'projects/mapbiomas-workspace/AUXILIAR/cartas'

assetMasks = "projects/mapbiomas-workspace/AUXILIAR/landsat-mask"

csvFile = './data/caatinga-collection-7.csv'

collectionIds = {
    'l4': 'LANDSAT/LT04/C02/T1_L2',
    'l5': 'LANDSAT/LT05/C02/T1_L2',
    'l7': 'LANDSAT/LE07/C02/T1_L2',
    'l8': 'LANDSAT/LC08/C02/T1_L2',
}

landsatIds = {
    'l4': 'landsat-4',
    'l5': 'landsat-5',
    'l7': 'landsat-7',
    'l8': 'landsat-8',
}

outputCollections = {
    'l4': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'l5': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'l7': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'l8': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2'
}

bufferSize = 100


def multiplyBy10000(image):

    bands = [
        'blue',
        'red',
        'green',
        'nir',
        'swir1',
        'swir2',
        'cai',
        'evi2',
        'gcvi',
        'hallcover',
        'hallheigth',
        'ndvi',
        'ndwi',
        'pri',
        'savi',
    ]

    return image.addBands(
        srcImg=image.select(bands).multiply(10000),
        names=bands,
        overwrite=True
    )


def divideBy10000(image):

    bands = [
        'blue',
        'red',
        'green',
        'nir',
        'swir1',
        'swir2'
    ]

    return image.addBands(
        srcImg=image.select(bands).divide(10000),
        names=bands,
        overwrite=True
    )


def applyCloudAndShadowMask(collection):

    # Get cloud and shadow masks
    collectionWithMasks = getMasks(collection,
                                   cloudThresh=10,
                                   cloudFlag=True,
                                   cloudScore=True,
                                   cloudShadowFlag=True,
                                   cloudShadowTdom=True,
                                   zScoreThresh=-1,
                                   shadowSumThresh=4000,
                                   dilatePixels=4,
                                   cloudHeights=[
                                       200, 700, 1200, 1700, 2200, 2700,
                                       3200, 3700, 4200, 4700
                                   ],
                                   cloudBand='cloudScoreMask')

    # get collection without clouds
    collectionWithoutClouds = collectionWithMasks \
        .map(
            lambda image: image.mask(
                image.select([
                    'cloudFlagMask',
                    'cloudScoreMask',
                    'cloudShadowFlagMask'  # ,
                    # 'cloudShadowTdomMask'
                ]).reduce(ee.Reducer.anyNonZero()).eq(0)
            )
        )

    return collectionWithoutClouds


def getTiles(collection):

    collection = collection.map(
        lambda image: image.set(
            'tile', {
                'path': image.get('WRS_PATH'),
                'row': image.get('WRS_ROW'),
                'id': ee.Number(image.get('WRS_PATH'))
                        .multiply(1000).add(image.get('WRS_ROW')).int32()
            }
        )
    )

    tiles = collection.distinct(['tile']).reduceColumns(
        ee.Reducer.toList(), ['tile']).get('list')

    return tiles.getInfo()


def getExcludedImages(biome, year):

    assetId = 'projects/mapbiomas-workspace/MOSAICOS/workspace-c5'

    collection = ee.ImageCollection(assetId) \
        .filterMetadata('region', 'equals', biome) \
        .filterMetadata('year', 'equals', str(year))

    excluded = ee.List(collection.reduceColumns(ee.Reducer.toList(), ['black_list']).get('list')) \
        .map(
            lambda names: ee.String(names).split(',')
    )

    return excluded.flatten().getInfo()


gee_toolbox.switch_user(ACCOUNT)
gee_toolbox.init()

# load csv file data
table = pd.read_csv(csvFile, delimiter=';')
table = table[(table['PROCESS'] == 1)]
table = table.sort_values(['YEAR'], ascending=False)

print(table)

# load grids asset
grids = ee.FeatureCollection(gridsAsset)

# get all tile names
collectionTiles = ee.ImageCollection(assetMasks)

allTiles = collectionTiles.reduceColumns(
    ee.Reducer.toList(), ['tile']).get('list').getInfo()

for row in table.itertuples():

    if row.BIOME in ["PAMPA", "CAATINGA"]:
        dateStart = datetime.strptime(row.T0_P, "%d/%m/%Y").strftime("%Y-%m-%d")
        dateEnd = datetime.strptime(row.T1_P, "%d/%m/%Y").strftime("%Y-%m-%d")
    else:
        dateStart = datetime.strptime(row.T0_P, "%Y-%m-%d").strftime("%Y-%m-%d")
        dateEnd = datetime.strptime(row.T1_P, "%Y-%m-%d").strftime("%Y-%m-%d")

    satelliteId = row.SATELLITE.lower()

    satellites = []

    if row.SATELLITE.lower() == 'lx':
        satellites = ['l5', 'l7']
    else:
        satellites = [row.SATELLITE.lower()]

    for satelliteId in satellites:

        try:
            # if True:
            alreadyInCollection = ee.ImageCollection(outputCollections[satelliteId]) \
                .filterMetadata('year', 'equals', int(row.YEAR)) \
                .filterMetadata('biome', 'equals', row.BIOME) \
                .reduceColumns(ee.Reducer.toList(), ['system:index']) \
                .get('list') \
                .getInfo()

            outputName = row.BIOME + '-' + \
                row.GRID_NAME + '-' + \
                str(row.YEAR) + '-' + \
                satelliteId.upper() + '-' + \
                str(version)
            
            if outputName not in alreadyInCollection:

                # define a geometry
                grid = grids.filterMetadata(
                    'grid_name', 'equals', row.GRID_NAME)

                grid = ee.Feature(grid.first()).geometry()\
                    .buffer(bufferSize).bounds()

                excluded = []
                if row.BIOME == 'PANTANAL':
                    excluded = getExcludedImages(row.BIOME, row.YEAR)

                # returns a collection containing the specified parameters
                collection = getCollection(collectionIds[satelliteId],
                                        dateStart='{}-{}'.format(row.YEAR, '01-01'),
                                        dateEnd='{}-{}'.format(row.YEAR, '12-31'),
                                        cloudCover=row.CC,
                                        geometry=grid,
                                        blacklist=excluded
                                        )
                
                # detect the image tiles
                tiles = getTiles(collection)
                tiles = list(
                    filter(
                        lambda tile: tile['id'] in allTiles,
                        tiles
                    )
                )

                subcollectionList = []

                if len(tiles) > 0:
                    # apply tile mask for each image
                    for tile in tiles:
                        print(tile['path'], tile['row'])

                        subcollection = collection \
                            .filterMetadata('WRS_PATH', 'equals', tile['path']) \
                            .filterMetadata('WRS_ROW', 'equals', tile['row'])

                        tileMask = ee.Image(
                            '{}/{}-{}'.format(assetMasks, tile['id'], versionMasks))

                        subcollection = subcollection.map(
                            lambda image: image.mask(tileMask).selfMask()
                        )

                        subcollectionList.append(subcollection)

                    # merge collections
                    collection = ee.List(subcollectionList) \
                        .iterate(
                            lambda subcollection, collection:
                                ee.ImageCollection(
                                    collection).merge(subcollection),
                            ee.ImageCollection([])
                    )

                    # flattens collections of collections
                    collection = ee.ImageCollection(collection)
                    
                    # returns a pattern of landsat collection 2 band names
                    bands = getBandNames(satelliteId + 'c2')

                    # Rename collection image bands
                    collection = collection.select(
                        bands['bandNames'],
                        bands['newNames']
                    )

                    collection = applyCloudAndShadowMask(collection)

                    endmember = ENDMEMBERS[landsatIds[satelliteId]]

                    collection = collection.map(
                        lambda image: image.addBands(
                            getFractions(image, endmember))
                    )

                    # calculate SMA indexes
                    collection = collection\
                        .map(getNDFI)\
                        .map(getSEFI)\
                        .map(getWEFI)\
                        .map(getFNS)

                    # calculate Spectral indexes
                    collection = collection\
                        .map(divideBy10000)\
                        .map(getCAI)\
                        .map(getEVI2)\
                        .map(getGCVI)\
                        .map(getHallCover)\
                        .map(getHallHeigth)\
                        .map(getNDVI)\
                        .map(getNDWI)\
                        .map(getPRI)\
                        .map(getSAVI)\
                        .map(multiplyBy10000)
                    
                    # generate mosaic
                    if row.BIOME in ['PANTANAL']:
                        percentileBand = 'ndwi'
                    else:
                        percentileBand = 'ndvi'

                    mosaic = getMosaic(collection,
                                        percentileDry=25,
                                        percentileWet=75,
                                        percentileBand=percentileBand,
                                        dateStart=dateStart,
                                        dateEnd=dateEnd)
                    
                    mosaic = getEntropyG(mosaic)
                    mosaic = getSlope(mosaic)
                    mosaic = setBandTypes(mosaic)

                    mosaic = mosaic.set('year', int(row.YEAR))
                    mosaic = mosaic.set('collection', 7.0)
                    mosaic = mosaic.set('grid_name', row.GRID_NAME)
                    mosaic = mosaic.set('version', str(version))
                    mosaic = mosaic.set('biome', row.BIOME)
                    mosaic = mosaic.set('satellite', satelliteId)

                    print(outputName)

                    task = ee.batch.Export.image.toAsset(
                        image=mosaic,
                        description=outputName,
                        assetId=outputCollections[satelliteId] + '/' + outputName,
                        region=grid.coordinates().getInfo(),
                        scale=30,
                        maxPixels=int(1e13),

                    )

                    task.start()

        except Exception as e:
            print(e)

        # ee.Reset()

gee_toolbox.switch_user('joao')
gee_toolbox.init()
