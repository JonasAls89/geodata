from flask import Flask, request, jsonify
import json
import requests
import logging
import yaml
import os
import sys

app = Flask(__name__)

logger = None

## On your local set the below env vars
os.environ['username'] = "<your username>"
os.environ['password'] = "<your password>"
os.environ['referrer'] = "arcgis.mydomain.com"

required_env_vars = ['username', 'password', 'referrer']
missing_env_vars = list() 

## Helper functions
def check_env_variables(required_env_vars, missing_env_vars):
    for env_var in required_env_vars:
        value = os.getenv(env_var)
        if not value:
            missing_env_vars.append(env_var)
        
    if len(missing_env_vars) != 0:
        app.logger.error(f"Missing the following required environment variable(s) {missing_env_vars}")
        sys.exit(1)

@app.route('/')
def index():
    output = {
        'service': 'Geodata.no Connector',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)

@app.route('/get_geo', methods=['GET'])
def get_data():
    ## Validating env vars
    check_env_variables(required_env_vars, missing_env_vars)
    ##

    payload = {
        'username' : os.getenv('username'),
        'password' : os.getenv('password'),
        'referrer' : os.getenv('referrer')
    }    

    ## Query parameters for dynamic fetching
    wkid = request.args['wkid']
    x = request.args['x']
    y = request.args['y']
    geometry_query = {"x":x, "y":y,"spatialReference":{"wkid":wkid}}

    ## Generating token and checking response
    generate_url = "https://services.geodataonline.no/arcgis/tokens/generateToken/query?username=%s&password=%s&referer=%s&f=pjson" % (payload['username'], payload['password'], payload['referrer'])
    check_response = requests.get(generate_url)
    if not check_response.ok:
        app.logger.error(f"Access token request failed. Error: {check_response.content}")
        raise
    valid_response = check_response.json()
    token = {'Authorization' : 'Bearer ' + valid_response['token']}
    ##

    ## Requesting geo data
    request_url = f"https://services.geodataonline.no/arcgis/rest/services/Geomap_UTM33_EUREF89/GeomapMatrikkel/MapServer/5/query?geometry={geometry_query}&geometryType=esriGeometryPoint&inSR={wkid}&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=kommunenr%2Cgardsnr%2Cbruksnr&returnGeometry=false&returnTrueCurves=false&returnIdsOnly=false&returnCountOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson"
    geo_data = requests.get(request_url, headers=token)
    if geo_data.status_code != 200:
        app.logger.error(f"Unexpected response status code: {geo_data.content}")
        raise
    ##

    return jsonify(geo_data.json())

if __name__ == '__main__':
    # Set up logging
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('geodata-microservice')

    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)