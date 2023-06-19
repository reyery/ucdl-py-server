def new_geojson_template():
    return {
        "type": "FeatureCollection",
        "features": []
    }


def new_geojson_polygon(coords):
    if len(coords) < 3 : return None
    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": []
            },
            "properties": {}
        }]
    }
    pgon_coords = []
    for c in coords:
        pgon_coords.append([float(c[0]), float(c[1])])
    if (coords[-1] != coords[0]):
        pgon_coords.append(pgon_coords[0])
    geojson['features'][0]['geometry']['coordinates'].append(pgon_coords)
    return geojson
