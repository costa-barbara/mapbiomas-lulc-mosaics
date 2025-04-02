
var assetPathRow = "users/joaovsiqueira1/sentinel-2-acquisition-plans";
var assetOrbit = "projects/mapbiomas-workspace/AUXILIAR/sentinel-2-orbit";

var geometry = ee.Geometry.Polygon(
    [
        [
            [-82.91763689923195, 13.496542967765722],
            [-82.91763689923195, -57.46855036794329],
            [-31.765293149231972, -57.46855036794329],
            [-31.765293149231972, 13.496542967765722]
        ]
    ], null, false);

var pathRow = ee.FeatureCollection(assetPathRow)
    .filter(ee.Filter.bounds(geometry));

var orbits = pathRow.aggregate_histogram('OrbitRelat').keys().getInfo();

print(orbits);

orbits.forEach(
    function (orbit) {

        var raster = ee.Image().paint(pathRow.filter(ee.Filter.eq('OrbitRelat', orbit)), 1);

        Map.addLayer(raster.multiply(ee.Number.parse(orbit)).randomVisualizer());

        Export.image.toAsset({
            image: raster.set('orbit', orbit),
            description: 'orbit-' + orbit,
            assetId: assetOrbit + '/' + 'orbit-' + orbit,
            pyramidingPolicy: { '.default': 'MODE' },
            region: geometry,
            scale: 10,
            maxPixels: 1e13
        }
        );
    }
);