from flask import Flask, request, jsonify, Response
from sesamutils import VariablesConfig 
import json
import requests
import logging
import os
import sys

app = Flask(__name__)

## Logic for running program in dev
try:
    with open("helpers.json", "r") as stream:
        env_vars = stream.read()
        os.environ["username"] = env_vars[20:35]
        os.environ["password"] = env_vars[56:67]
        os.environ["referrer"] = env_vars[88:107]
    stream.close()
except OSError as e:
    app.logger.info("Using env vars defined in SESAM")

username = os.getenv('username')
password = os.getenv('password')
referrer = os.getenv('referrer')

logger = None
required_env_vars = ['username', 'password', 'referrer']

default_response = {
    "geodata": {
            'kommunenr': u'NaN',
            'gardsnr': u'NaN',
            'bruksnr': u'NaN'
        }
}

## Helper functions
def stream_json(clean):
    first = True
    yield '['
    for i, row in enumerate(clean):
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(row)
    yield ']'


## Merge helper function
def dict_merger(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res 


@app.route('/')
def index():
    output = {
        'service': 'Geodata.no Connector',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)


@app.route('/geo_data', methods=['GET','POST'])
def get_data():
    config = VariablesConfig(required_env_vars)
    if not config.validate():
        sys.exit(1)

    app.logger.info(f"The geodata-connector is running")

    request_body = request.get_json()

    payload = {
        'username' : username,
        'password' : password,
        'referrer' : referrer
    }

    ## Generating token and checking response
    generate_url = "https://services.geodataonline.no/arcgis/tokens/generateToken/query?username=%s&password=%s&referer=%s&f=pjson" % (payload['username'], payload['password'], payload['referrer'])
    check_response = requests.get(generate_url)
    if not check_response.ok:
        app.logger.error(f"Access token request failed. Error: {check_response.content}")
        raise
    valid_response = check_response.json()
    token = {'Authorization' : 'Bearer ' + valid_response['token']}
    ##

    return_object = [] 
    for element in request_body:
        try:
            ## Query parameters for dynamic fetching
            wkid = str(element.get("wkid"))
            x = str(element.get('x_coordinate'))
            y = str(element.get('y_coordinate'))
            if '~f' in x or y:
                x = x.strip('~f')
                y = y.strip('~f')
            app.logger.info(f"The x, y and wkid respectively '{x}', '{y}', '{wkid}'")

            if not x or not y:
                app.logger.warning(f"The x or y coordinates '{x}', '{y}' are not provided in the right format")
            geometry_query = {"x":x, "y":y,"spatialReference":{"wkid":wkid}}

            ## Requesting geo data
            request_url = f"https://services.geodataonline.no/arcgis/rest/services/Geomap_UTM33_EUREF89/GeomapMatrikkel/MapServer/5/query?geometry={geometry_query}&geometryType=esriGeometryPoint&inSR={wkid}&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=kommunenr%2Cgardsnr%2Cbruksnr&returnGeometry=false&returnTrueCurves=false&returnIdsOnly=false&returnCountOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson"
            #app.logger.info(request_url)
            geo_data = requests.get(request_url, headers=token)
            if not geo_data.ok:
                app.logger.error(f"Unexpected response status code: {geo_data.content}")
                return f"Unexpected error : {geo_data.content}", 500
                raise
            #app.logger.info(f"returning call with status code {geo_data.json()}")
            try:
                geo_transform = geo_data.json()['features'][0]
                geo_transform["geodata"] = geo_transform.pop("attributes")
            except IndexError as e:
                app.logger.error(f"exiting with error {e}")
                geo_transform = default_response
            except KeyError as e:
                app.logger.error(f"exiting with error {e}")
                geo_transform = default_response
            sesam_dict = dict_merger(dict(element), dict(geo_transform))
            return_object.append(sesam_dict)
            ##
        except Exception as e:
            app.logger.warning(f"Service not working correctly. Failing with error : {e}")

    return Response(stream_json(return_object), mimetype='application/json')

if __name__ == '__main__':
    # Set up logging
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('geodata-connector')

    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)