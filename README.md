# Geodata-Connector

## This is a repo for connecting to geodata.no

## To install requirements run the following

```
yarn install
```

## the following auth helpers you need to set as env variables

i.e.

```
os.environ['username'] = <your username>
os.environ['password'] = <your password>
os.environ['referrer'] = arcgis.mydomain.com
```

## To run the app :
in package.json you'll find the
commands needed to run the app.

## Config in Sesam

## System example :

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

## Pipe example :

1. Name the pipe ```geodataconnector-ms```

2. Config :
```
{
  "_id": "geodataconnector-ms",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "geodata-connector",
    "url": "/get_geo?wkid=3857&x=<x-coordinate>&y=<y-coordinate>"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"],
        ["create",
          ["apply", "create-entity", "_S.attributes"]
        ],
        ["discard"]
      ],
      "create-entity": [
        ["copy", "*"]
      ]
    }
  }
}
```