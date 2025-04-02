#
import ee
import sys
import os

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('../gee_toolbox'))

import gee as gee_toolbox
from modules.Mosaic import *
from modules.DataType import *
from modules.BandNames import *
from modules.Collection import *
from modules.SmaAndNdfi import *
from modules.Miscellaneous import *
from modules.SpectralIndexes import *
from modules.CloudAndShadowMask import *

# Import modules

ee.Initialize()

# Set up account to use
ACCOUNT = 'joao'

versionMasks = '2'

gridsAsset = 'projects/mapbiomas-workspace/AUXILIAR/cartas'

assetMasks = "projects/mapbiomas-workspace/AUXILIAR/landsat-mask"

# nome do bioma sem espaço
themeNames = [
    'URBANO',
    # 'URBANO-TEST'
]

version = {
    'URBANO': '2',
    'URBANO-TEST': '2',
}

dataFilter = {
    'URBANO-TEST': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
    'URBANO': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
}

gridNames = {
    "URBANO": [
        "NA-19", "NA-20", "NA-21", "NA-22", "NB-20", "NB-21", "NB-22", "SA-19",
        "SA-20", "SA-21", "SA-22", "SA-23", "SA-24", "SB-18", "SB-19", "SB-20",
        "SB-21", "SB-22", "SB-23", "SB-24", "SB-25", "SC-18", "SC-19", "SC-20",
        "SC-21", "SC-22", "SC-23", "SC-24", "SC-25", "SD-20", "SD-21", "SD-22",
        "SD-23", "SD-24", "SE-20", "SE-21", "SE-22", "SE-23", "SE-24", "SF-21",
        "SF-22", "SF-23", "SF-24", "SG-21", "SG-22", "SG-23", "SH-21", "SH-22",
        "SI-22"
    ],
    "URBANO-TEST": [
        'SF-23',
    ]
}

collectionIds = {
    'l5': 'LANDSAT/LT05/C01/T1_SR',
    'l7': 'LANDSAT/LE07/C01/T1_SR',
    'l8': 'LANDSAT/LC08/C01/T1_SR',

    'l5_DN': 'LANDSAT/LT05/C01/T1',
    'l7_DN': 'LANDSAT/LE07/C01/T1',
    'l8_DN': 'LANDSAT/LC08/C01/T1',
}

landsatIds = {
    'l5': 'landsat-5',
    'l7': 'landsat-7',
    'l8': 'landsat-8',
}

outputCollections = {
    'l5': 'projects/nexgenmap/MapBiomas2/LANDSAT/mosaics-urban-test',
    'l7': 'projects/nexgenmap/MapBiomas2/LANDSAT/mosaics-urban-test',
    'l8': 'projects/nexgenmap/MapBiomas2/LANDSAT/mosaics-urban-test'
}

bufferSize = 100

yearsSat = [
    # [2020, 'l8'], [2019, 'l8'], [2018, 'l8'],
    # [2017, 'l8'], [2016, 'l8'], [2015, 'l8'],
    # [2014, 'l8'], [2013, 'l8'],

    # [2011, 'l5'], [2010, 'l5'], [2009, 'l5'],
    # [2008, 'l5'], [2007, 'l5'], [2006, 'l5'],
    # [2005, 'l5'], [2004, 'l5'], [2003, 'l5'],
    # [2002, 'l5'], [2001, 'l5'], [2000, 'l5'],
    # [1999, 'l5'], [1998, 'l5'], [1997, 'l5'],
    # [1996, 'l5'], [1995, 'l5'], [1994, 'l5'],
    # [1993, 'l5'], [1992, 'l5'], [1991, 'l5'],
    # [1990, 'l5'], [1989, 'l5'], [1988, 'l5'],
    # [1987, 'l5'], [1986, 'l5'], [1985, 'l5'],

    [2012, 'l7'],
    [2002, 'l7'], [2001, 'l7'], [2000, 'l7'],
    [2005, 'l7'], [2004, 'l7'], [2003, 'l7'],
    # [2020, 'l7'], [2019, 'l7'], [2018, 'l7'],
    # [2017, 'l7'], [2016, 'l7'], [2015, 'l7'],
    # [2014, 'l7'], [2013, 'l7'], 
    # [2011, 'l7'], [2010, 'l7'], [2009, 'l7'],
    # [2008, 'l7'], [2007, 'l7'], [2006, 'l7'],
]


def multiplyBy10000(image):
    
    bands = [
        'blue', 
        'red', 
        'green', 
        'nir', 
        'swir1', 
        'swir2',
        'tir',
        'evi',
        'ndvi',
        'ndwi',
        'mndwi',
        'ndbi',
        'ui',
        'bu',
        # 'ebbi',
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
        'swir2',
        'tir'
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
                    # 'cloudScoreMask',
                    'cloudShadowFlagMask'#,
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

# get all tile names
collectionTiles = ee.ImageCollection(assetMasks)

allTiles = collectionTiles.reduceColumns(
    ee.Reducer.toList(), ['tile']).get('list').getInfo()

for themeName in themeNames:

    grids = ee.FeatureCollection(gridsAsset)
    
    for year, satellite in yearsSat:

        dateStart = '{}-{}'.format(year, dataFilter[themeName]['dateStart'])
        dateEnd = '{}-{}'.format(year, dataFilter[themeName]['dateEnd'])
        cloudCover = dataFilter[themeName]['cloudCover']

        for gridName in gridNames[themeName]:

            try:
            # if True:
                alreadyInCollection = ee.ImageCollection(outputCollections[satellite]) \
                    .filterMetadata('year', 'equals', year) \
                    .filterMetadata('biome', 'equals', themeName) \
                    .reduceColumns(ee.Reducer.toList(), ['system:index']) \
                    .get('list') \
                    .getInfo()

                outputName = 'URBAN-' + \
                    gridName + '-' + \
                    str(year) + '-' + \
                    satellite.upper() + '-' + \
                    str(version[themeName])

                if outputName not in alreadyInCollection:

                    # define a geometry
                    # grid = grids.filterMetadata(
                    #     'grid_name', 'equals', gridName)
                    
                    grid = grids.filter(
                        ee.Filter.stringContains('grid_name', gridName))

                    grid = grid.geometry()\
                        .buffer(bufferSize).bounds()

                    # returns a collection containing the specified parameters
                    collection = getCollection(collectionIds[satellite],
                                               dateStart='{}-{}'.format(year, '01-01'),
                                               dateEnd='{}-{}'.format(year, '12-31'),
                                               cloudCover=cloudCover,
                                               geometry=grid
                                               )
                    
                    collectionDN = getCollection(collectionIds[satellite + '_DN'],
                                               dateStart='{}-{}'.format(year, '01-01'),
                                               dateEnd='{}-{}'.format(year, '12-31'),
                                               cloudCover=cloudCover,
                                               collectionType='DN',
                                               geometry=grid
                                               )

                    collection = collection.combine(collectionDN)
                    
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

                        # returns a pattern of band names
                        bands = getBandNames(satellite + '_urban')
                        
                        # Rename collection image bands
                        collection = collection.select(
                            bands['bandNames'],
                            bands['newNames']
                        )
                        
                        collection = applyCloudAndShadowMask(collection)

                        endmember = ENDMEMBERS[landsatIds[satellite]]
                        endmemberSmall = ENDMEMBERS['small']

                        collection = collection.map(
                            lambda image: image
                                .addBands(getFractions(image, endmember))
                                .addBands(getFractionsSmall(image, endmemberSmall))
                        )

                        # calculate SMA indexes
                        collection = collection\
                            .map(getNDFI)

                        # calculate Spectral indexes
                        collection = collection\
                            .map(divideBy10000)\
                            .map(getEVI)\
                            .map(getNDVI)\
                            .map(getNDWI)\
                            .map(getMNDWI)\
                            .map(getNDBI)\
                            .map(getUI)\
                            .map(getBU)\
                            .map(getEBBI)\
                            .map(multiplyBy10000)

                        # generate mosaic
                        mosaic = getMosaicUrban(collection,
                                                percentiles=[1,99],
                                                percentilesSlice=[25,75],
                                                sliceBand='ndvi')
                        
                        mosaic = setBandTypes(mosaic, mtype='urban')
                        
                        mosaic = mosaic.set('year', year)
                        mosaic = mosaic.set('collection', 6.0)
                        mosaic = mosaic.set('grid_name', gridName)
                        mosaic = mosaic.set('version', str(version[themeName]))
                        mosaic = mosaic.set('biome', themeName)
                        mosaic = mosaic.set('satellite', satellite)
                        mosaic = mosaic.set('theme', 'urban')

                        print(outputName)

                        task = ee.batch.Export.image.toAsset(
                            image=mosaic,
                            description=outputName,
                            assetId=outputCollections[satellite] +
                            '/' + outputName,
                            region=grid.coordinates().getInfo(),
                            scale=30,
                            maxPixels=int(1e13)
                        )

                        task.start()

            except Exception as e:
                print(e)

            # ee.Reset()

gee_toolbox.switch_user('joao')
gee_toolbox.init()
