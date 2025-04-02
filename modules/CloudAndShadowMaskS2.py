#!/usr/bin/env python

# Import earthengine API
import ee
import math

from modules.CloudAndShadowMask import cloudFlagMask
ee.Initialize()


def tdom(collection,
         zScoreThresh=-1,
         shadowSumThresh=5000,
         dilatePixels=2):

    shadowSumBands = ['nir', 'swir1']

    irStdDev = collection \
        .select(shadowSumBands) \
        .reduce(ee.Reducer.stdDev())

    irMean = collection \
        .select(shadowSumBands) \
        .mean()

    def _maskDarkOutliers(image):
        zScore = image.select(shadowSumBands) \
            .subtract(irMean) \
            .divide(irStdDev)

        irSum = image.select(shadowSumBands) \
            .reduce(ee.Reducer.sum())

        tdomMask = zScore.lt(zScoreThresh) \
            .reduce(ee.Reducer.sum()) \
            .eq(2) \
            .And(irSum.lt(shadowSumThresh)) \

        tdomMask = tdomMask.focal_min(dilatePixels)

        return image.addBands(tdomMask.rename('tdomMask'))

    collection = collection.map(_maskDarkOutliers)

    return collection


def cloudProject(image,
                 cloudBand=None,
                 shadowSumThresh=0.5,
                 cloudHeights=[],
                 dilatePixels=2):

    cloud = image.select([cloudBand])

    # Get TDOM mask
    tdomMask = image.select(['tdomMask'])

    darkPixels = image.select(['blue', 'green', 'red', 'nir', 'swir1', 'swir2']) \
        .reduce(ee.Reducer.sum()) \
        .lt(shadowSumThresh)

    nominalScale = cloud.projection().nominalScale()

    meanAzimuth = image.get('sun_azimuth_angle')
    meanElevation = image.get('sun_elevation_angle')

    azR = ee.Number(meanAzimuth) \
        .multiply(math.pi) \
        .divide(180.0) \
        .add(ee.Number(0.5).multiply(math.pi))

    zenR = ee.Number(0.5) \
        .multiply(math.pi) \
        .subtract(ee.Number(meanElevation).multiply(math.pi).divide(180.0))

    def _findShadow(cloudHeight):
        cloudHeight = ee.Number(cloudHeight)

        shadowCastedDistance = zenR.tan() \
            .multiply(cloudHeight)

        x = azR.cos().multiply(shadowCastedDistance) \
            .divide(nominalScale).round()

        y = azR.sin().multiply(shadowCastedDistance) \
            .divide(nominalScale).round()

        return cloud.changeProj(cloud.projection(), cloud.projection().translate(x, y))

    shadows = ee.List(cloudHeights).map(_findShadow)

    shadow = ee.ImageCollection.fromImages(shadows).max().unmask()
    shadow = shadow.focal_max(dilatePixels)
    shadow = shadow.And(darkPixels).And(tdomMask.Not().And(cloud.Not()))

    shadowMask = shadow.rename(['cloudShadowTdomMask'])

    return image.addBands(shadowMask)


def getMasks(collection,
             zScoreThresh=-1,
             shadowSumThresh=5000,
             dilatePixels=2,
             cloudHeights=[]):
    """"Get cloud and shadow masks.

    Parameters:
        collection (ee.Image): collection TOA or SR containing at least the bands:
            blue, green, red, nir, swir1, swir2 and quality band
        zScoreThresh (int): 
        shadowSumThresh (int): 
        dilatePixels (int): number of pixels to buffering clouds
        cloudFlag (boolean): if True, create a cloud mask using quality band. Defaults to True.
        cloudScore (boolean): if True, create a cloud mask using simple cloud score algorithm. Defaults to True.
        cloudShadowFlag (boolean): if True, create a cloud shadow mask using quality band. Defaults to True.
        cloudShadowTdom (boolean): if True, create a cloud shadow mask using TDOM algorithm. Defaults to True.
        cloudHeights (list): list containing the cloud heights
        cloudBand (str): index band name to be used

    Returns:
        ee.ImageCollection: collection with cloud/shadow masks
    """

    collection = ee.Algorithms.If(
        cloudFlag,
        ee.Algorithms.If(
            cloudScore,
            collection.map(cloudFlagMask).map(
                lambda collection: cloudScoreMask(collection, cloudThresh)
            ),
            collection.map(cloudFlagMask)),
        collection.map(
            lambda collection: cloudScoreMask(collection, cloudThresh)
        )
    )

    collection = ee.ImageCollection(collection)

    collection = ee.Algorithms.If(
        cloudShadowFlag,
        ee.Algorithms.If(
            cloudShadowTdom,
            tdom(collection.map(cloudShadowFlagMask),
                 zScoreThresh=zScoreThresh,
                 shadowSumThresh=shadowSumThresh,
                 dilatePixels=dilatePixels),
            collection.map(cloudShadowFlagMask)),
        tdom(collection,
             zScoreThresh=zScoreThresh,
             shadowSumThresh=shadowSumThresh,
             dilatePixels=dilatePixels))

    collection = ee.ImageCollection(collection)

    def _getShadowMask(image):

        image = cloudProject(image,
                             shadowSumThresh=shadowSumThresh,
                             dilatePixels=dilatePixels,
                             cloudHeights=cloudHeights,
                             cloudBand=cloudBand)

        return image

    if cloudShadowTdom:
        collection = collection.map(_getShadowMask)

    return collection
