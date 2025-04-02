from pprint import pprint
import ee
import sys
import os

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath('../'))

from modules.Mosaic import *
from modules.DataType import *
from modules.BandNames import *
from modules.Collection import *
from modules.SmaAndNdfi import *
from modules.Miscellaneous import *
from modules.SpectralIndexes import *
from modules.CloudAndShadowMaskS2 import *

ee.Initialize()

ASSET_GRIDS = 'projects/mapbiomas-workspace/AUXILIAR/cim-world-1-250000'

ASSET_ORBITS = 'projects/mapbiomas-workspace/AUXILIAR/sentinel-2-orbit'

COLLECTION_ID = 5

# nome do bioma sem espaço
regionNames = [
    'ECUADOR',
    'VENEZUELA',
]

version = {
    'ECUADOR': '1',
    'VENEZUELA': '1',
}

CLOUD_PROBABILITY = {
    'ECUADOR': 40,
    'VENEZUELA': 40,
}

dataFilter = {
    'ECUADOR': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
    'VENEZUELA': {
        'dateStart': '01-01',
        'dateEnd': '12-31',
        'cloudCover': 80
    },
}

gridNames = {
    "ECUADOR": [
        # 'NA-18-Y-D',
        # 'SA-17-X-B',
        'SA-17-Z-D'
    ],
    "VENEZUELA": [
        # 'NB-20-X-C',
        # 'NB-20-X-D',
        # 'NB-20-Z-A',
        # 'NB-20-Z-B',
        # 'NB-20-Z-C',
    ],
}

collectionIds = {
    's2_toa': 'COPERNICUS/S2',
    's2': 'COPERNICUS/S2_SR',
    's2_harmonized': 'COPERNICUS/S2_HARMONIZED',
}

sentinelIds = {
    's2_toa': 'sentinel-2 (toa)',
    's2_harmonized': 'sentinel-2 (harmonized)',
}

outputCollections = {
    's2_harmonized': 'projects/nexgenmap/MapBiomas2/SENTINEL/PANAMAZON/mosaics-1',
}

bufferSize = 100

yearsSat = [
    [2016, 's2_harmonized'],
    [2017, 's2_harmonized'],
    [2018, 's2_harmonized'],
    [2019, 's2_harmonized'],
    [2020, 's2_harmonized'],
    [2021, 's2_harmonized'],
    [2022, 's2_harmonized'],
]

S2_CLOUD_PROBABILITY = 'COPERNICUS/S2_CLOUD_PROBABILITY'


def multiplyBy10000(image):

    bands = [
        'blue',
        'green',
        'red_edge_1',
        'red_edge_2',
        'red_edge_3',
        'red',
        'red_edge_4',
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
        'green',
        'red_edge_1',
        'red_edge_2',
        'red_edge_3',
        'red',
        'red_edge_4',
        'nir',
        'swir1',
        'swir2',
    ]

    return image.addBands(
        srcImg=image.select(bands).divide(10000),
        names=bands,
        overwrite=True
    )


def maskEdges(primary, secondary, leftField, rightField):
    """
    """
    joined = ee.Join.saveFirst('orbit')\
        .apply(primary=primary,
               secondary=secondary,
               condition=ee.Filter.equals(
                   leftField=leftField,
                   rightField=rightField
        )
    )
    
    joined = ee.ImageCollection(joined)
    
    joined = joined.map(
        lambda image: ee.Image(image).multiply(
            ee.Image(ee.Image(image).get('orbit')))
                .copyProperties(image)
                .copyProperties(image, ['system:time_start'])
    )

    return ee.ImageCollection(joined)


def applyCloudMask(collection, dateStart, dateEnd, geometry, maxCloudProbability=40):

    def _getCloudMask(image):

        clouds = image.select(['probability'])

        cloudMask = clouds.gt(maxCloudProbability)\
            .rename(['cloudMask'])

        return image.addBands(cloudMask)

    def _getShadowMask(image):

        image = cloudProject(image,
                             shadowSumThresh=6000,
                             dilatePixels=2,
                             cloudHeights=[
                                 200, 700, 1200, 1700, 2200, 2700,
                                 3200, 3700, 4200, 4700
                             ],
                             cloudBand='cloudMask')

        return image

    criteria = ee.Filter.date(dateStart, dateEnd)

    cloudProbability = ee.ImageCollection(S2_CLOUD_PROBABILITY)\
        .filter(criteria)\
        .filterBounds(grid)

    collectionWithCloudMask = ee.ImageCollection(collection.combine(cloudProbability))\
        .map(_getCloudMask)

    collectionWithCloudMask = tdom(collectionWithCloudMask,
                                   zScoreThresh=-1,
                                   shadowSumThresh=6000,
                                   dilatePixels=2)

    collectionWithCloudMask = collectionWithCloudMask.map(_getShadowMask)

    collectionWithoutClouds = collectionWithCloudMask \
        .map(
            lambda image: image.mask(
                image.select([
                    'cloudMask',
                    'cloudShadowTdomMask'
                ]).reduce(ee.Reducer.anyNonZero()).eq(0)
            )
        )

    return collectionWithoutClouds


orbits = ee.ImageCollection(ASSET_ORBITS)\
    .map(lambda image: image.set('orbit', ee.Number.parse(image.get('orbit'))))

for regionName in regionNames:

    for year, satellite in yearsSat:

        grids = ee.FeatureCollection(ASSET_GRIDS)\
            .filter(
            ee.Filter.inList('name', gridNames[regionName])
        )

        dateStart = '{}-{}'.format(year, dataFilter[regionName]['dateStart'])
        dateEnd = '{}-{}'.format(year, dataFilter[regionName]['dateEnd'])
        cloudCover = dataFilter[regionName]['cloudCover']
        
        for gridName in gridNames[regionName]:

            try:
                # if True:
                alreadyInCollection = ee.ImageCollection(outputCollections[satellite]) \
                    .filterMetadata('year', 'equals', year) \
                    .filterMetadata('territory', 'equals', regionName) \
                    .reduceColumns(ee.Reducer.toList(), ['system:index']) \
                    .get('list') \
                    .getInfo()

                outputName = regionName + '-' + \
                    gridName + '-' + \
                    str(year) + '-' + \
                    str(version[regionName])

                if outputName not in alreadyInCollection:
                    # define a geometry
                    grid = grids.filter(ee.Filter.stringContains(
                        'name', gridName))

                    grid = ee.Feature(grid.first()).geometry()\
                        .buffer(bufferSize).bounds()

                    # returns a collection containing the specified parameters
                    collection = getCollection(collectionIds[satellite],
                                               dateStart=str(year) + '-01-01',
                                               dateEnd=str(year) + '-12-30',
                                               cloudCover=70,
                                               geometry=grid,
                                               scaleFactor=False
                                               )

                    # returns a pattern of band names
                    bands = getBandNames(satellite)

                    # Rename collection image bands
                    collection = collection.select(
                        bands['bandNames'],
                        bands['newNames']
                    )

                    endmember = ENDMEMBERS[sentinelIds[satellite]]

                    collection = applyCloudMask(collection,
                                                dateStart=dateStart,
                                                dateEnd=dateEnd,
                                                geometry=grid,
                                                maxCloudProbability=CLOUD_PROBABILITY[regionName])

                    collection = collection.map(
                        lambda image: getFractions(image, endmember))
                    
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
                    
                    # remove noised edges
                    collection = maskEdges(
                        primary=collection,
                        secondary=orbits,
                        leftField='SENSING_ORBIT_NUMBER',
                        rightField='orbit'
                    )

                    # generate mosaic
                    if regionName in ['PANTANAL']:
                        percentileBand = 'ndwi'
                    else:
                        percentileBand = 'ndvi'

                    mosaic = getMosaic(collection,
                                       percentileDry=25,
                                       percentileWet=75,
                                       percentileBand=percentileBand,
                                       dateStart=dateStart,
                                       dateEnd=dateEnd)

                    mosaic = getSlope(mosaic)
                    mosaic = getEntropyG(mosaic)
                    mosaic = setBandTypes(mosaic, mtype="biomes_s2")

                    mosaic = mosaic.set('year', year)
                    mosaic = mosaic.set('collection', COLLECTION_ID)
                    mosaic = mosaic.set('grid_name', gridName)
                    mosaic = mosaic.set('version', str(version[regionName]))
                    mosaic = mosaic.set('territory', regionName)
                    mosaic = mosaic.set('satellite', satellite)

                    print(outputName)

                    task = ee.batch.Export.image.toAsset(
                        image=mosaic,
                        description=outputName,
                        assetId=outputCollections[satellite] +
                        '/' + outputName,
                        region=grid.coordinates().getInfo(),
                        scale=10,
                        maxPixels=int(1e13)
                    )

                    task.start()

            except Exception as e:
                print(e)
