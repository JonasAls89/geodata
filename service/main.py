from flask import Flask, request, jsonify, Response
from sesamutils import VariablesConfig, sesam_logger 
import json
import requests
import os
import sys

app = Flask(__name__)
logger = sesam_logger("Steve the logger", app=app)

## Logic for running program in dev
try:
    with open("helpers.json", "r") as stream:
        env_vars = stream.read()
        os.environ["username"] = env_vars[20:35]
        os.environ["password"] = env_vars[56:67]
        os.environ["referrer"] = env_vars[88:107]
    stream.close()
except OSError as e:
    logger.info("Using env vars defined in SESAM")

username = os.getenv('username')
password = os.getenv('password')
referrer = os.getenv('referrer')

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


def get_token(payload):
    ## Generating token and checking response
    generate_url = "https://services.geodataonline.no/arcgis/tokens/generateToken/query?username=%s&password=%s&referer=%s&f=pjson" % (payload['username'], payload['password'], payload['referrer'])
    check_response = requests.get(generate_url)
    if not check_response.ok:
        logger.error(f"Access token request failed. Error: {check_response.content}")
        raise
    valid_response = check_response.json()
    return valid_response
    ##


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

    logger.info(f"The geodata-connector is running")

    request_data = request.get_data()
    json_data = json.loads(str(request_data.decode("utf-8")))

    valid_response = None
    payload = {
        'username' : username,
        'password' : password,
        'referrer' : referrer
    }

    return_object = []
    for element in json_data[0].get("payload"):
        if valid_response == None:
            logger.info("Requesting access token...")
            valid_response = get_token(payload)
            token = {'Authorization' : 'Bearer ' + valid_response['token']}
        if valid_response['expires'] <= 10:
            logger.info("Refreshing access token...")
            valid_response = get_token(payload)
            token = {'Authorization' : 'Bearer ' + valid_response['token']}
        try:
            ## Query parameters for dynamic fetching
            wkid = str(element.get("wkid"))
            x = str(element.get('x_coordinate'))
            y = str(element.get('y_coordinate'))
            if '~f' in x or y:
                x = x.strip('~f')
                y = y.strip('~f')
            logger.info(f"The x, y and wkid respectively '{x}', '{y}', '{wkid}'")

            if not x or not y:
                logger.warning(f"The x or y coordinates '{x}', '{y}' are not provided in the right format")
            geometry_query = {"x":x, "y":y,"spatialReference":{"wkid":wkid}}

            ## Requesting geo data
            request_url = f"https://services.geodataonline.no/arcgis/rest/services/Geomap_UTM33_EUREF89/GeomapMatrikkel/MapServer/5/query?geometry={geometry_query}&geometryType=esriGeometryPoint&inSR={wkid}&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=kommunenr%2Cgardsnr%2Cbruksnr&returnGeometry=false&returnTrueCurves=false&returnIdsOnly=false&returnCountOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson"
            geo_data = requests.get(request_url, headers=token)
            if not geo_data.ok:
                logger.error(f"Unexpected response status code: {geo_data.content}")
                return f"Unexpected error : {geo_data.content}", 500
                raise

            try:
                geo_transform = geo_data.json()['features'][0]
                geo_transform["geodata"] = geo_transform.pop("attributes")
            except IndexError as e:
                logger.error(f"exiting with error {e}")
                geo_transform = default_response
            except KeyError as e:
                logger.error(f"exiting with error {e}")
                geo_transform = default_response
            sesam_dict = dict_merger(dict(element), dict(geo_transform))
            return_object.append(sesam_dict)
            ##
        except Exception as e:
            logger.warning(f"Service not working correctly. Failing with error : {e}")

    transform_response = []
    if json_data[0].get("_id"):
        return_dictionary = {
        "_id": f"{json_data[0].get('_id')}",
        "geo_response": return_object
        }
        transform_response.append(return_dictionary)
    else:
        logger.info(f"No _id provided in payload...")
        return_dictionary = { "geo_response": return_object }
        transform_response.append(return_dictionary)

    return Response(stream_json(transform_response), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)