import ee

ee.Initialize()

assetInput = "projects/earthengine-legacy/assets/projects/mapbiomas-indonesia/MOSAICS/workspace-c1"
assetOutput = "projects/nexgenmap/MapBiomas2/LANDSAT/INDONESIA/mosaics-1"

collectionIn = ee.ImageCollection(assetInput)
collectionOut = ee.ImageCollection(assetOutput)

namesIn = collectionIn.aggregate_array('system:index').getInfo()
namesOut = collectionOut.aggregate_array('system:index').getInfo()

for name in namesIn:
    print(name)

    if name not in namesOut:
        sourceId = assetInput + '/' + name
        destinationId = assetOutput + '/' + name
        
        try:
            # print(sourceId, destinationId)
            ee.data.copyAsset(sourceId=sourceId, destinationId=destinationId)
        except Exception as e:
            print(e)
