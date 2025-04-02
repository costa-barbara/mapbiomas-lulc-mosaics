
var nsLatPositions = [
    ['N', 1],
    ['S', -1]
];

var nsLatDeg = 4; // 4 graus de norte a sul
var ewLonDeg = 6; // 6 graus de lesta a oeste

var rows = [
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V'
];

var zones = Array.apply(0, Array(60)).map(function (_, b) { return b + 1; })

var geometries = nsLatPositions.map(
    function (nsLatPosition) {

        var geometries = zones.map(
            function (zone, z) {

                var leftLon = (zone * ewLonDeg) - ewLonDeg;
                var rightLon = (zone * ewLonDeg);

                if (zone <= 30) {
                    leftLon = leftLon - 180;
                    rightLon = rightLon - 180;
                } else {
                    leftLon = leftLon + 180;
                    rightLon = rightLon + 180;
                }

                var geometries = rows.map(
                    function (row, i) {

                        var upperLat = nsLatPosition[1] * nsLatDeg * (i + 1);
                        var lowerLat = nsLatPosition[1] * nsLatDeg * (i + 1);

                        if (nsLatPosition[1] > 0) {
                            lowerLat = lowerLat - nsLatDeg;
                        } else {
                            upperLat = upperLat + nsLatDeg;
                        }

                        var geometry = ee.Geometry.Polygon(
                            [
                                [
                                    [leftLon, upperLat], // UL
                                    [leftLon, lowerLat], // LL
                                    [rightLon, lowerLat],  // LR
                                    [rightLon, upperLat]   // UR
                                ]
                            ], null, false);

                        var name = nsLatPosition[0].concat(row).concat('-').concat(zone.toString());

                        return ee.Feature(geometry).set('name', name);
                    }
                );

                geometries = ee.FeatureCollection(geometries);

                return geometries
            }
        );

        geometries = ee.FeatureCollection(geometries).flatten();

        return geometries;
    }
);

geometries = ee.FeatureCollection(geometries).flatten()
// .filter(ee.Filter.bounds(point));

var vxyzGeometries = geometries
    .map(
        function (feature) {
            var coords = ee.List(feature.geometry().coordinates().get(0));

            // var v1 = ee.List(coords.get(0)); // LL 
            // var v2 = ee.List(coords.get(1)); // LR
            // var v3 = ee.List(coords.get(2)); // UR
            var v4 = ee.List(coords.get(3)); // UL
            // var v5 = ee.List(coords.get(4)); // LL

            var vGeometry = ee.Geometry.Polygon([
                /*LL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(2)],
                /*LR*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(2)],
                /*UR*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(0)],
                /*UL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(0)],
                /*LL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(2)],
            ]);

            var xGeometry = ee.Geometry.Polygon([
                /*LL*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(2)],
                /*LR*/[ee.Number(v4.get(0)).add(6), ee.Number(v4.get(1)).subtract(2)],
                /*UR*/[ee.Number(v4.get(0)).add(6), ee.Number(v4.get(1)).subtract(0)],
                /*UL*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(0)],
                /*LL*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(2)],
            ]);

            var yGeometry = ee.Geometry.Polygon([
                /*LL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(4)],
                /*LR*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(4)],
                /*UR*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(2)],
                /*UL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(2)],
                /*LL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(4)],
            ]);

            var zGeometry = ee.Geometry.Polygon([
                /*LL*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(4)],
                /*LR*/[ee.Number(v4.get(0)).add(6), ee.Number(v4.get(1)).subtract(4)],
                /*UR*/[ee.Number(v4.get(0)).add(6), ee.Number(v4.get(1)).subtract(2)],
                /*UL*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(2)],
                /*LL*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(4)],
            ]);

            var name = ee.String(feature.get('name'));

            var vName = name.cat('-V');
            var vFeature = ee.Feature(vGeometry).set('name', vName);

            var xName = name.cat('-X');
            var xFeature = ee.Feature(xGeometry).set('name', xName);

            var yName = name.cat('-Y');
            var yFeature = ee.Feature(yGeometry).set('name', yName);

            var zName = name.cat('-Z');
            var zFeature = ee.Feature(zGeometry).set('name', zName);

            return ee.FeatureCollection([vFeature, xFeature, yFeature, zFeature]);
        }
    );

vxyzGeometries = ee.FeatureCollection(vxyzGeometries).flatten()

// print(vxyzGeometries);

var abcdGeometries = vxyzGeometries
    .map(
        function (feature) {
            var coords = ee.List(feature.geometry().coordinates().get(0));

            // var v1 = ee.List(coords.get(0)); // LL 
            // var v2 = ee.List(coords.get(1)); // LR
            // var v3 = ee.List(coords.get(2)); // UR
            var v4 = ee.List(coords.get(3)); // UL
            // var v5 = ee.List(coords.get(4)); // LL

            var aGeometry = ee.Geometry.Polygon([
                /*LL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(1)],
                /*LR*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(1)],
                /*UR*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(0)],
                /*UL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(0)],
                /*LL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(1)],
            ]);

            var bGeometry = ee.Geometry.Polygon([
                /*LL*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(1)],
                /*LR*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(1)],
                /*UR*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(0)],
                /*UL*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(0)],
                /*LL*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(1)],
            ]);

            var cGeometry = ee.Geometry.Polygon([
                /*LL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(2)],
                /*LR*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(2)],
                /*UR*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(1)],
                /*UL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(1)],
                /*LL*/[ee.Number(v4.get(0)).add(0), ee.Number(v4.get(1)).subtract(2)],
            ]);

            var dGeometry = ee.Geometry.Polygon([
                /*LL*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(2)],
                /*LR*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(2)],
                /*UR*/[ee.Number(v4.get(0)).add(3), ee.Number(v4.get(1)).subtract(1)],
                /*UL*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(1)],
                /*LL*/[ee.Number(v4.get(0)).add(1.5), ee.Number(v4.get(1)).subtract(2)],
            ]);

            var name = ee.String(feature.get('name'));

            var aName = name.cat('-A');
            var aFeature = ee.Feature(aGeometry).set('name', aName);

            var bName = name.cat('-B');
            var bFeature = ee.Feature(bGeometry).set('name', bName);

            var cName = name.cat('-C');
            var cFeature = ee.Feature(cGeometry).set('name', cName);

            var dName = name.cat('-D');
            var dFeature = ee.Feature(dGeometry).set('name', dName);

            return ee.FeatureCollection([aFeature, bFeature, cFeature, dFeature]);
        }
    );

abcdGeometries = ee.FeatureCollection(abcdGeometries).flatten()

// print(abcdGeometries);

var vis = { opacity: 0.5 };

Map.addLayer(geometries, vis);
Map.addLayer(vxyzGeometries, vis);
Map.addLayer(abcdGeometries, vis);

Export.table.toAsset(
    abcdGeometries,
    'cim-world-1-250000',
    'projects/mapbiomas-workspace/AUXILIAR/cim-world-1-250000'
);
Export.table.toAsset(
    vxyzGeometries,
    'cim-world-1-500000',
    'projects/mapbiomas-workspace/AUXILIAR/cim-world-1-500000'
);
Export.table.toAsset(
    geometries,
    'cim-world-1-1000000',
    'projects/mapbiomas-workspace/AUXILIAR/cim-world-1-1000000'
);