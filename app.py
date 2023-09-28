# import main Flask class and request object
import os
import time 
from flask import Flask, request, send_from_directory
from flask_cors import CORS, cross_origin
from simulations.AH_dispersion.AH_dispersion import run_AH_dispersion
from simulations.urban_wind.urban_wind import run_urban_wind, run_urban_wind_upload
from simulations.wind.wind import run_wind
from simulations.wind.wind_clip import run_wind_clip
from simulations.sky.sky import run_sky
from simulations.solar.solar import run_solar
from simulations.air_pollutant.air_pollutant import run_air_pollutant, get_ap

# from simulations.util.geojson_to_feature import geojson_to_feature
import subprocess

# create the Flask app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
if not os.path.exists('./temp_result'):
   os.makedirs('./temp_result')

def create_upload_geojson(data):
    for i in data:
        print(i)


@app.route('/ah', methods=['POST'])
def ah():
    print('~~~~~~~~~~~~~')
    # path = os.getcwd() + '\\AH_dispersion_result\\'
    request_data = request.get_json()

    bounds = request_data['bounds']
    print('........', str(bounds).replace(' ', ''))
    # subprocess.run(["powershell", "pwd"], shell=True)

    result = run_AH_dispersion(bounds)
    return result

@app.route('/uwind', methods=['POST'])
def uwind():
    print('~~~~~~~~~~~~~')
    # path = os.getcwd() + '\\AH_dispersion_result\\'
    request_data = request.get_json()

    bounds = request_data['bounds']
    print('........', str(bounds).replace(' ', ''))
    # subprocess.run(["powershell", "pwd"], shell=True)

    result = run_urban_wind(bounds)
    return result

@app.route('/solar', methods=['POST'])
def solar():
    print('~~~~~~~~~~~~~')
    # path = os.getcwd() + '\\AH_dispersion_result\\'
    request_data = request.get_json()

    print('........', request_data)

    bounds = request_data['bounds']
    grid_size = request_data['grid_size']
    # subprocess.run(["powershell", "pwd"], shell=True)

    result = run_solar(bounds, grid_size)
    return result

@app.route('/wind', methods=['POST'])
def wind():
    print('~~~~~~~~~~~~~')
    # path = os.getcwd() + '\\AH_dispersion_result\\'
    request_data = request.get_json()

    print('........', request_data)

    bounds = request_data['bounds']
    grid_size = request_data['grid_size']
    # subprocess.run(["powershell", "pwd"], shell=True)

    result = run_wind(bounds, grid_size)
    return result

@app.route('/wind_clip', methods=['POST'])
def wind_clip():
    print('~~~~~~~~~~~~~')
    # path = os.getcwd() + '\\AH_dispersion_result\\'
    request_data = request.get_json()

    print('........', request_data)

    bounds = request_data['bounds']
    grid_size = request_data['grid_size']
    # subprocess.run(["powershell", "pwd"], shell=True)

    result = run_wind_clip(bounds, grid_size)
    return result


@app.route('/sky', methods=['POST'])
def sky():
    print('~~~~~~~~~~~~~')
    # path = os.getcwd() + '\\AH_dispersion_result\\'
    request_data = request.get_json()

    bounds = request_data['bounds']
    grid_size = request_data['grid_size']
    print('........', str(bounds).replace(' ', ''))
    # subprocess.run(["powershell", "pwd"], shell=True)

    result = run_sky(bounds, grid_size)
    return result

@app.route('/ap', methods=['POST'])
def ap():
    print('~~~~~~~~~~~~~')
    # path = os.getcwd() + '\\AH_dispersion_result\\'
    request_data = request.get_json()

    bounds = request_data['bounds']
    print('........', str(bounds).replace(' ', ''))
    # subprocess.run(["powershell", "pwd"], shell=True)

    result = run_air_pollutant(bounds)
    return result

###############################################

@app.route('/ah_upload', methods=['POST'])
def ah_up():
    print('~~~~~~~~~~~~~')
    request_data = request.get_json()
    print('request_data', request_data)

    # bounds = request_data['bounds']
    # print('........', str(bounds).replace(' ', ''))
    return {}

@app.route('/uwind_upload', methods=['POST'])
def uwind_up():
    print('~~~~~~~~~~~~~')
    request_data = request.get_json()

    session = str(time.time_ns())
    # print('request_data', request_data)

    sim_bound = request_data['simBoundary']
    print('........ simBoundary', str(sim_bound).replace(' ', ''))

    feat_bound = request_data['featureBoundary']
    print('........ featureBoundary', str(feat_bound).replace(' ', ''))

    data = request_data['data']
    # print('........ data', str(data).replace(' ', ''))

    # data_tif = geojson_to_feature(session, data, sim_bound, feat_bound)
    # result = run_urban_wind_upload(session, data_tif, sim_bound)

    return {}


# @app.route('/sky_upload', methods=['POST'])
# def sky_up():
#     print('~~~~~~~~~~~~~')
#     request_data = request.get_json()
#     print('request_data', request_data)

#     bounds = request_data['bounds']
#     print('........', str(bounds).replace(' ', ''))
#     return {}

# @app.route('/ap_upload', methods=['POST'])
# def ap_up():
#     print('~~~~~~~~~~~~~')
#     request_data = request.get_json()
#     print('request_data', request_data)

#     bounds = request_data['bounds']
#     print('........', str(bounds).replace(' ', ''))
#     return {}

###############################################

@app.route('/get_ap', methods=['GET'])
def ap_get():
    return get_ap()


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=False, host='0.0.0.0', port=5000)
