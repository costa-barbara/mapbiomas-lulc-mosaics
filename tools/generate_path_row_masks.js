
[
    // [221, 67],
    // [221, 68],
    // [221, 69],
    // [221, 70],
    // [222, 67],
    // [222, 68],
    // [222, 69],
    // [222, 70],
    // [223, 67],
    // [223, 68],
    // [223, 69],
    // [223, 70],
    // [224, 67],
    // [224, 68],
    // [224, 69],
    // [224, 70],
    // [217, 66],
    // [217, 67],
    // [217, 68],
    // [218, 66],
    // [218, 67],
    // [218, 68],
    [224, 82],
    // [220, 80],
    // [221, 80],
    // [222, 80],
].forEach(
    function (pathRow) {

        var collection = ee.ImageCollection("LANDSAT/LT05/C01/T1_TOA")
            .filterDate('2000-01-01', '2011-12-31')
            .filterMetadata('WRS_PATH', 'equals', pathRow[0])
            .filterMetadata('WRS_ROW', 'equals', pathRow[1]);
        // .filter(ee.Filter.stringContains('system:index', '226067'));

        var collectionMasks = collection
            .select('B2')
            .map(
                function (image) {
                    return image.mask();
                }
            );

        var centroids = collection.map(
            function (image) {
                return image.geometry().centroid();
            }
        );

        centroids = ee.FeatureCollection(centroids);

        var centroid = centroids.geometry().centroid();

        var azimuth = collection.aggregate_mean('SUN_AZIMUTH');

        var centroidCoords = centroid.coordinates();
        var centroidX = ee.Number(centroidCoords.get(0));
        var centroidY = ee.Number(centroidCoords.get(1));

        // var bounds = centroid.buffer(86000).bounds();

        var deltaX = 87 / 111;
        var deltaY = 85 / 111;

        var bounds = [
            [centroidX.subtract(deltaX), centroidY.subtract(deltaY)],
            [centroidX.add(deltaX), centroidY.subtract(deltaY)],
            [centroidX.add(deltaX), centroidY.add(deltaY)],
            [centroidX.subtract(deltaX), centroidY.add(deltaY)],
            [centroidX.subtract(deltaX), centroidY.subtract(deltaY)]
        ];

        var rotatedCoords = ee.List(bounds/*.coordinates().get(0)*/).map(
            function (coord) {
                var x = ee.Number(ee.List(coord).get(0)).subtract(centroidX);
                var y = ee.Number(ee.List(coord).get(1)).subtract(centroidY);

                var theta = ee.Number(-0.18)/*azimuth.subtract(90)*/
                // var theta = azimuth.subtract(90)

                var xr = x.multiply(theta.cos()).subtract(y.multiply(theta.sin()));
                var yr = x.multiply(theta.sin()).add(y.multiply(theta.cos()));

                return ee.List([xr.add(centroidCoords.get(0)), yr.add(centroidCoords.get(1))]);
            }
        );

        var rotatedPolygon = ee.Geometry.Polygon(ee.List([rotatedCoords]));

        var mask = collectionMasks.product();

        Map.addLayer(collection, {
            bands: 'B5,B4,B3',
            gain: '800,600,2000'
        }, 'collection', false);

        Map.addLayer(rotatedPolygon, { color: 'red' }, 'rotated', true, 0.3);
    }
)