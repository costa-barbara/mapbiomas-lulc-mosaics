import ee
import sys
import os

sys.path.append(os.path.abspath('../'))

from modules.CloudAndShadowMaskC2 import *
from modules.SpectralIndexes import *
from modules.Miscellaneous import *
from modules.SmaAndNdfi import *
from modules.Collection import *
from modules.BandNames import *
from modules.DataType import *
from modules.Mosaic import *

sys.dont_write_bytecode = True

ee.Initialize()


versionMasks = '2'

gridsAsset = 'projects/mapbiomas-workspace/AUXILIAR/CHILE/grids'

assetMasks = "projects/mapbiomas-workspace/AUXILIAR/landsat-mask"

# nome do bioma sem espaço
territoryNames = [
    'CHILE'
]

version = {
    'CHILE': '2',
}

dataFilter = {
    'CHILE': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
}

gridNames = {
    "CHILE": [
        "SE-19-V-D", "SE-19-Y-B", "SE-19-Y-D", "SE-19-Z-C",
        "SF-19-Y-D", "SF-19-Z-C", "SF-19-Z-D", "SG-19-V-A",
        "SG-19-Z-A", "SG-19-Y-C", "SG-19-Y-D", "SG-19-Z-C",
        "SI-19-V-A", "SI-19-V-B", "SI-19-V-C", "SI-19-V-D",
        "SJ-19-V-B", "SJ-18-X-C", "SJ-18-X-D", "SJ-19-V-C",
        "SK-18-X-C", "SK-18-X-D", "SK-19-V-C", "SK-18-Z-A",
        "SL-18-V-D", "SL-18-X-C", "SL-18-X-D", "SL-19-V-C",
        "SM-18-V-B", "SM-18-X-A", "SM-18-X-B", "SM-18-V-D",
        "SM-19-Y-C", "SM-19-Y-D", "SN-18-V-B", "SN-18-X-A",
        "SN-19-X-C", "SN-18-Z-B", "SN-19-Y-A", "SN-19-Y-B",
        "SF-19-V-B", "SF-19-X-A", "SF-19-V-D", "SF-19-X-C",
        "SF-19-Y-B", "SF-19-Z-A", "SF-19-Z-B", "SF-19-Y-C",
        "SG-19-V-B", "SG-19-X-A", "SG-19-X-B", "SG-19-V-C",
        "SG-19-V-D", "SG-19-X-C", "SG-19-Y-A", "SG-19-Y-B",
        "SH-19-V-A", "SH-19-V-B", "SH-19-V-C", "SH-19-V-D",
        "SH-19-Y-A", "SH-19-Y-B", "SH-19-Y-C", "SH-19-Y-D",
        "SI-18-Z-B", "SI-19-Y-A", "SI-19-Y-B", "SI-18-Z-D",
        "SI-19-Y-C", "SI-19-Y-D", "SJ-18-X-B", "SJ-19-V-A",
        "SJ-18-Z-B", "SJ-19-Y-A", "SJ-18-Z-C", "SJ-18-Z-D",
        "SJ-19-Y-C", "SK-18-X-A", "SK-18-X-B", "SK-19-V-A",
        "SK-18-Z-B", "SK-19-Y-A", "SK-18-Z-C", "SK-18-Z-D",
        "SK-19-Y-C", "SL-18-X-A", "SL-18-X-B", "SL-19-V-A",
        "SL-18-Y-B", "SL-18-Z-A", "SL-18-Z-B", "SL-19-Y-A",
        "SL-18-Y-D", "SL-18-Z-C", "SL-18-Z-D", "SL-19-Y-C",
        "SM-18-X-C", "SM-18-X-D", "SM-18-Y-B", "SM-18-Z-A",
        "SM-18-Z-B", "SM-18-Y-D", "SM-18-Z-C", "SM-18-Z-D",
        "SN-18-X-B", "SN-19-V-A", "SN-19-V-B", "SN-19-X-A",
        "SN-18-X-C", "SN-18-X-D", "SN-19-V-C", "SN-19-V-D",
        "SN-19-Z-A", "SN-19-Z-B", "SN-19-Y-C", "SN-19-Y-D",
        "SN-19-Z-C", "SN-19-Z-D"
    ],
}

collectionIds = {
    'l4': 'LANDSAT/LT04/C02/T1_L2',
    'l5': 'LANDSAT/LT05/C02/T1_L2',
    'l7': 'LANDSAT/LE07/C02/T1_L2',
    'l8': 'LANDSAT/LC08/C02/T1_L2',
    'l9': 'LANDSAT/LC09/C02/T1_L2',
}

landsatIds = {
    'l4': 'landsat-4',
    'l5': 'landsat-5',
    'l7': 'landsat-7',
    'l8': 'landsat-8',
    'l9': 'landsat-9',
}

outputCollections = {
    'l4': 'projects/mapbiomas-chile/assets/MOSAICS/mosaics-2',
    'l5': 'projects/mapbiomas-chile/assets/MOSAICS/mosaics-2',
    'l7': 'projects/mapbiomas-chile/assets/MOSAICS/mosaics-2',
    'l8': 'projects/mapbiomas-chile/assets/MOSAICS/mosaics-2',
    'l9': 'projects/mapbiomas-chile/assets/MOSAICS/mosaics-2'
}

bufferSize = 100

yearsSat = [
    # [2022, 'l8'],
    # [2021, 'l8'], [2020, 'l8'], [2019, 'l8'],
    # [2018, 'l8'], [2017, 'l8'], [2016, 'l8'],
    # [2015, 'l8'], [2014, 'l8'], [2013, 'l8'],
    # [2011, 'l5'], [2010, 'l5'], [2009, 'l5'],
    # [2008, 'l5'], [2007, 'l5'], [2006, 'l5'],
    # [2005, 'l5'], [2004, 'l5'], [2003, 'l5'],
    [2002, 'l5'], [2001, 'l5'], [2000, 'l5'],
    [1999, 'l5'], [1998, 'l5'], [1997, 'l5'],
    [1996, 'l5'], [1995, 'l5'], [1994, 'l5'],
    [1993, 'l5'], [1992, 'l5'], [1991, 'l5'],
    [1990, 'l5'], [1989, 'l5'], [1988, 'l5'],
    [1987, 'l5'], [1986, 'l5'], [1985, 'l5'],
    [2012, 'l7'], 
    [2003, 'l7'],
    [2002, 'l7'], [2001, 'l7'], [2000, 'l7'],
    # [2005, 'l7'], [2004, 'l7'], 
    # [2020, 'l7'], [2019, 'l7'], [2018, 'l7'],
    # [2017, 'l7'], [2016, 'l7'], [2015, 'l7'],
    # [2021, 'l7'],
    # [2014, 'l7'], [2013, 'l7'],
    # [2011, 'l7'], [2010, 'l7'], [2009, 'l7'],
    # [2008, 'l7'], [2007, 'l7'], [2006, 'l7'],
    # [1982, 'l4'], [1983, 'l4'], [1984, 'l4'],
]


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
                                   cloudBand='cloudShadowFlagMask')

    # get collection without clouds
    collectionWithoutClouds = collectionWithMasks \
        .map(
            lambda image: image.mask(
                image.select([
                    'cloudFlagMask',
                    'cloudShadowFlagMask'  # ,
                    # 'cloudScoreMask',
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


# get all tile names
collectionTiles = ee.ImageCollection(assetMasks)

allTiles = collectionTiles.reduceColumns(
    ee.Reducer.toList(), ['tile']).get('list').getInfo()

for territoryName in territoryNames:

    grids = ee.FeatureCollection(gridsAsset)\
        .filter(
        ee.Filter.inList('grid_name', gridNames[territoryName])
    )

    for year, satellite in yearsSat:

        dateStart = '{}-{}'.format(year, dataFilter[territoryName]['dateStart'])
        dateEnd = '{}-{}'.format(year, dataFilter[territoryName]['dateEnd'])
        cloudCover = dataFilter[territoryName]['cloudCover']

        for gridName in gridNames[territoryName]:
            
            try:
            # if True:
                alreadyInCollection = ee.ImageCollection(outputCollections[satellite]) \
                    .filterMetadata('year', 'equals', year) \
                    .filterMetadata('territory', 'equals', territoryName) \
                    .reduceColumns(ee.Reducer.toList(), ['system:index']) \
                    .get('list') \
                    .getInfo()
                
                outputName = territoryName + '-' + \
                    gridName + '-' + \
                    str(year) + '-' + \
                    satellite.upper() + '-' + \
                    str(version[territoryName])
                
                if outputName not in alreadyInCollection:
                    
                    # define a geometry
                    grid = grids.filter(ee.Filter.eq(
                        'grid_name', gridName))

                    grid = ee.Feature(grid.first()).geometry()\
                        .buffer(bufferSize).bounds()

                    excluded = []

                    # returns a collection containing the specified parameters
                    collection = getCollection(collectionIds[satellite],
                                               dateStart='{}-{}'.format(year, '01-01'),
                                               dateEnd='{}-{}'.format(year, '12-31'),
                                               cloudCover=cloudCover,
                                               geometry=grid,
                                               trashList=excluded
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
                        bands = getBandNames(satellite + 'c2')

                        # Rename collection image bands
                        collection = collection.select(
                            bands['bandNames'],
                            bands['newNames']
                        )

                        collection = applyCloudAndShadowMask(collection)

                        endmember = ENDMEMBERS[landsatIds[satellite]]

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
                        if territoryName in ['PANTANAL']:
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

                        mosaic = mosaic.set('year', year)
                        mosaic = mosaic.set('collection', 1.0)
                        mosaic = mosaic.set('grid_name', gridName)
                        mosaic = mosaic.set('version', str(version[territoryName]))
                        mosaic = mosaic.set('territory', territoryName)
                        mosaic = mosaic.set('satellite', satellite)

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
                msg = 'Too many tasks already in the queue (3000). Please wait for some of them to complete.'
                if e == msg:
                    raise Exception(e)
                else:
                    print(e)
