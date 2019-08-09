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

1. Name the system ```get-geodata```

2. Config :
```
{
  "_id": "get-geodata",
  "type": "system:microservice",
  "docker": {
    "image": "<docker username>/get-geodata:latest",
    "port": 5000
  },
  "verify_ssl": true
}
```

## Pipe example :

1. Name the pipe ```getgeodata-ms```

2. Config :
```
{
  "_id": "getgeodata-ms",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "get-geodata",
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