from flask import Flask, request, jsonify
import json
import requests
import yaml

app = Flask(__name__)

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
    ## Generating token
    stream = open('auth_headers.yml', 'r')
    settings = yaml.load(stream, yaml.SafeLoader)
    headers = {
        'username': "{0}".format(settings['username']),
        'password': "{0}".format(settings['password']),
        'referrer': "{0}".format(settings['referrer'])
    }
    genereateToken = "https://services.geodataonline.no/arcgis/tokens/generateToken/query?username=%s&password=%s&referer=%s&f=pjson" % (headers['username'], headers['password'], headers['referrer'])
    headerToken = requests.get(genereateToken).json()
    token = {'Authorization' : 'Bearer ' + headerToken['token']}
    
    ## Requesting geo data
    request_url = "https://services.geodataonline.no/arcgis/rest/services/Geomap_UTM33_EUREF89/GeomapMatrikkel/MapServer/5/query?geometry=%7B%22x%22%3A485817%2C%22y%22%3A6478206%2C%22spatialReference%22%3A%7B%22wkid%22%3A25832%7D%7D&geometryType=esriGeometryPoint&inSR=25832&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=kommunenr%2Cgardsnr%2Cbruksnr&returnGeometry=false&returnTrueCurves=false&returnIdsOnly=false&returnCountOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson"
    test = requests.get(request_url, headers=token)
    return jsonify(test.json())

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)