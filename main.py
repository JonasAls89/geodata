from flask import Flask, request, jsonify
import json
import requests
import yaml
import os

app = Flask(__name__)

os.environ['username'] = "<your username>"
os.environ['password'] = "your password"
os.environ['referrer'] = "arcgis.mydomain.com"

env = os.environ.get

@app.route('/')
def index():
    output = {
        'service': 'Geodata.no Connector',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)

@app.route('/get_geo', methods=['GET'])
def get_data():
    wkid = request.args['wkid']
    x = request.args['x']
    y = request.args['y']
    geometryQuery = {"x":x, "y":y,"spatialReference":{"wkid":wkid}}
    
    ## Generating token
    headers = {
        'username': "{0}".format(env('username')),
        'password': "{0}".format(env('password')),
        'referrer': "{0}".format(env('referrer'))
    }
    genereateToken = "https://services.geodataonline.no/arcgis/tokens/generateToken/query?username=%s&password=%s&referer=%s&f=pjson" % (headers['username'], headers['password'], headers['referrer'])
    headerToken = requests.get(genereateToken).json()
    token = {'Authorization' : 'Bearer ' + headerToken['token']}
    
    ## Requesting geo data
    request_url = f"https://services.geodataonline.no/arcgis/rest/services/Geomap_UTM33_EUREF89/GeomapMatrikkel/MapServer/5/query?geometry={geometryQuery}&geometryType=esriGeometryPoint&inSR={wkid}&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=kommunenr%2Cgardsnr%2Cbruksnr&returnGeometry=false&returnTrueCurves=false&returnIdsOnly=false&returnCountOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson"
    test = requests.get(request_url, headers=token)
    return jsonify(test.json())

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)