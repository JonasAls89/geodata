# Geodata-Connector

## This is a repo for connecting to geodata.no
This repo allows you to send a wkid and x and y coordinates from SESAM and then in return get kommunenr, gårdsnr og bruksnr on the /geo_data route.

## Routes:

```/geo_data```

```/fylke```

## How to:

*Run program in development*

This repo uses the file ```package.json``` and [yarn](https://yarnpkg.com/lang/en/) to run the required commands.

1. Make sure you have installed yarn.
2. Creata a file called ```helpers.json``` and set username, password and referrer in the following format:
```
{
    "username": "some username",
    "password": "some password",
    "referrer": "referrer url",
    "fylke_id": "some int",
    "attributes": "kommunenr,gardsnr,bruksnr,festenr",
    "base_url": "https://services.geodataonline.no/arcgis"
}
```
3. run:
    ```
        yarn install
    ```
4. execute to run the script:
    ```
        yarn swagger
    ```

## Expected payload on the /geo_data route:

```

 [{ "payload": [{
 "wkid": "3857",
    "x_coordinate": "~f924159.9248",
    "y_coordinate": "~f8025279.145"	
 },{
 	"wkid": "3857",
    "x_coordinate": "~f933165.1418",
    "y_coordinate": "~f8020815.2854"
 }]
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
    "referrer": "$ENV(arcgis.mydomain.com)",
    "base_url":"https://services.geodataonline.no/arcgis",
    "fylke_id": "<number>",
    "attributes": "<string_elements_comma_separated>" i.e. kommunenr,gardsnr,bruksnr,festenr
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
      "payload": [
        {
      "wkid": 3857,
      "x_coordinate": "~f994142.1292",
      "y_coordinate": "~f8152855.6122"
        }]
    }]
  },
  "transform": {
    "type": "chained",
    "transforms": [{
      "type": "dtl",
      "rules": {
        "default": [
          ["add", "::payload",
            ["map",
              ["dict", "_id", "_S._id", "x_coordinate",
                ["nth", 0,
                  ["nth", 0, "_."]
                ], "y_coordinate",
                ["nth", 0,
                  ["nth", 1, "_."]
                ], "wkid", 3857],
              ["first", "_S.geometry.netbas-cable:paths"]
            ]
          ]
        ]
      }
    }, {
      "type": "http",
      "system": "geodata-connector",
      "url": "/geo_data"
    }]
  },
  "pump": {
    "mode": "manual"
  },
  "namespaced_identifiers": true
}
```