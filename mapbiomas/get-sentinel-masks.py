
import ee

ee.Initialize()

assetPathRow = "users/joaovsiqueira1/sentinel-2-acquisition-plans"
assetGrids = "projects/mapbiomas-workspace/AUXILIAR/cartas"

assetOutput = "projects/mapbiomas-workspace/AUXILIAR/sentinel-2-mask"

grids = ee.FeatureCollection(assetGrids)
pathRow = ee.FeatureCollection(assetPathRow)

gridNames = grids.aggregate_array('grid_name').getInfo()

for gridName in gridNames:

    grid = grids.filter(ee.Filter.eq('grid_name', gridName))\
        .geometry()\
        .buffer(300)\
        .bounds()

    pathRowsSelected = pathRow.filter(ee.Filter.bounds(grid))

    pathRowsId = pathRowsSelected.aggregate_array('OrbitAbsol').getInfo()

    for pathRowId in pathRowsId:

        pathRowFeature = pathRowsSelected.filter(
            ee.Filter.eq('OrbitAbsol', pathRowId))

        raster = ee.Image().byte().paint(
            featureCollection=pathRowFeature,
            color=1
        )

        assetid = gridName + '-' + str(pathRowId)

        print(assetid)

        task = ee.batch.Export.image.toAsset(
            image=raster.byte().set('grid_name', gridName).set('orbit', pathRowId),
            description=assetid,
            assetId=assetOutput + '/' + assetid,
            region=grid.coordinates().getInfo(),
            scale=10,
            maxPixels=int(1e13)
        )

        task.start()
