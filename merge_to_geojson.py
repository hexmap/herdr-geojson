#!/usr/bin/env
# HexMap, 2020
# Written by Kyle Fitzsimmons
from datetime import datetime
import json
import os

DATA_DIR = './data'


points_feature_collection = {
    'type': 'FeatureCollection',
    'features': []
}

polylines_feature_collection = {
    'type': 'FeatureCollection',
    'features': []
}


date_idx = 0
last_date = None
polyline = None
# iterate over files containing individual points
for fn in sorted(os.listdir(DATA_DIR)):
    fp = os.path.join(DATA_DIR, fn)

    if not fn.endswith('GEOLOCATION.json'):
        continue

    with open(fp, 'r') as json_f:
        data = json.load(json_f)

        epoch = float(data['timestampEpoch']) / 1000
        dt = datetime.fromtimestamp(epoch)

        ## Polyline
        # create a new polyline feature by each day
        if not last_date or last_date != dt.date():
            if polyline:
                polylines_feature_collection['features'].append(polyline)

            polyline = {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': []
                },
                'properties': {
                    'date': dt.date().isoformat(),
                    'startTimestamp': data['timestamp'],
                    'endTimestamp': None,
                }
            }
            last_date = dt.date()
        polyline['properties']['endTimestamp'] = data['timestamp']
        polyline['geometry']['coordinates'].append([data['longitude'], data['latitude']])

        ## Point
        # generate a point data from each file
        point = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [data['longitude'], data['latitude']]
            },
            'properties': {
                'timestamp': data['timestamp'],
                'timestampEpoch': data['timestampEpoch'],
                'altitude': data['altitude'],
                'accuracyHorizontalMeters': data['accuracyHorizontalMeters'],
                'accuracyVerticalMeters': data['accuracyVerticalMeters']
            }
        }
        points_feature_collection['features'].append(point)

# append last polyline before loop was terminated
polylines_feature_collection['features'].append(polyline)



# write output files
with open('points.geojson', 'w') as geojson_points_f:
    json.dump(points_feature_collection, geojson_points_f)

with open('polylines.geojson', 'w') as geojson_polylines_f:
    json.dump(polylines_feature_collection, geojson_polylines_f)


