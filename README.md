# Geodata-Connector

## This is a repo for connecting to geodata.no
This repo allows you to send a wkid and x and y coordinates from SESAM and then in return get kommunenr, gårdsnr og bruksnr.

### To install requirements run the following

```
yarn install
```

### The following auth helpers need to be set as env variables

i.e.

```
os.environ['username'] = <your username>
os.environ['password'] = <your password>
os.environ['referrer'] = arcgis.mydomain.com
```

### To run the app :
in package.json you'll find the
commands needed to run the app.

## Expected payload on the /geo_data route:

```

 [{
 "wkid": "3857",
    "x_coordinate": "~f924159.9248",
    "y_coordinate": "~f8025279.145"	
 },{
 	"wkid": "3857",
    "x_coordinate": "~f933165.1418",
    "y_coordinate": "~f8020815.2854"
 }]

```

### Config in Sesam

#### System example :

1. Name the system ```geodata-connector```

2. Config :

```
{
  "_id": "geodata-connector",
  "type": "system:microservice",
  "docker": {
    "image": "<docker username>/geodata-connector:latest",
    "port": 5000,
    "username": "$ENV(<username for geodata account>)",
    "password": "$ENV(<password for geodata account>)",
    "referrer": "$ENV(arcgis.mydomain.com)"
  },
  "verify_ssl": true
}
```

#### Pipe example :

1. Name the pipe ```geodataconnector-ms```

2. Config :

```
{
  "_id": "geodataconnector-ms",
  "type": "pipe",
  "source": {
    "type": "embedded",
    "entities": [{
      "_id": "<your ID>",
      "wkid": 3857,
      "x_coordinate": "~f994142.1292",
      "y_coordinate": "~f8152855.6122"
    }]
  },
  "transform": {
    "type": "chained",
    "transforms": [{
      "type": "dtl",
      "rules": {
        "default": [
          ["copy", "*"],
          ["add", "::x_coordinate", "_S.x_coordinate"],
          ["add", "::y_coordinate", "_S.y_coordinate"],
          ["add", "::wkid", "_S.wkid"]
        ]
      }
    }, {
      "type": "http",
      "system": "geodata-connector",
      "batch_size": 1,
      "url": "/geo_data"
    }]
  },
  "pump": {
    "mode": "manual"
  },
  "namespaced_identifiers": true
}
```