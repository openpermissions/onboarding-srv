FORMAT: 1A
HOST: https://on-stage.copyrighthub.org

# Open Permissions Platform Onboarding Service
The Onboarding Service is a simple service used to onboard data to the Hub.

## Standard error output
On endpoint failure there is a standard way to report errors.
The output should be of the form

| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| errors   | A list of errors          | array  |

### Error
| Property       | Description                                 | Type   | Mandatory |
| :-------       | :----------                                 | :---   | :-------  |
| source         | The name of the service producing the error | number | yes       |
| message        | A description of the error                  | string | yes       |
| source_id_type | The type of the source identity             | string | no        |
| line           | The line the error occurred                 | number | no        |

# Authorization

This API requires authentication. Where [TOKEN] is indicated in an endpoint header you should supply an OAuth 2.0 access token with the appropriate scope (read, write or delegate). 

See [How to Auth](https://github.com/openpermissions/auth-srv/blob/master/documents/markdown/how-to-auth.md) 
for details of how to authenticate Hub services.

# Group Service information
Information on the service

## Onboarding service information [/v1/onboarding]

### Retrieve service information [GET]

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | The service information   | object |

##### Service information
| Property            | Description                      | Type   |
| :-------            | :----------                      | :---   |
| service_name        | The name of the api service      | string |
| version             | The version of the api service   | string |
| service_id          | The ID of the onboarding service | string |
| default_resolver_id | The ID of the resolver           | string |
| hub_id              | The ID of the hub                | string |

+ Request
    + Headers

            Accept: application/json

+ Response 200 (application/json; charset=UTF-8)
    + Body

            {
                "status": 200,
                "data": {
                    "service_name": "Open Permissions Platform Onboarding Service",
                    "version": "0.1.0",
                    "service_id": "d6e29563e22311e5b45cacbc32a8c615",
                    "default_resolver_id": "copyrighthub.org",
                    "hub_id": "hub1"
                }
            }

# Group Capabilities
Capabilities/limitations of the service

## Onboarding service capabilities [/v1/onboarding/capabilities]

### Retrieve service capabilities [GET]

| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | The service capabilities  | object |

##### Service capabilities
| Property      | Description           | Type   |
| :-------      | :----------           | :---   |
| max_file_size | The maximum file size | number |

+ Request
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 200 (application/json; charset=UTF-8)
    + Body

            {
                "status": 200,
                "data": {
                    "max_file_size": 11000000
                }
            }


# Group Assets

## Onboard assets [/v1/onboarding/repositories/{repository_id}/assets{?r2rml_url}]

+ Parameters
    + repository_id (required, string)
        ID for the repository where the date should stored
    + r2rml_url (optional, url)
        url for an r2rml mapping file. The mapping file should be an RDF graph in Turtle syntax expressing the logic for transforming the original CSV or JSON data into an RDF document using the Open Permissions Ontology.

### Onboard rights data for assets to a repository [POST]

| OAuth Token Scope |
| :----------       |
| write             |

#### Input

Multiple id types can be onboarded for a given asset. The first id type and value will be used to form the hub key, and the rest will be registered as aliases.

Item n of the source_id_types must correspond with item n of source_ids.

An optional parameter r2rml_url for a url to an r2rml mappings file can be supplied to apply customised transformation.

If the parameter is not supplied, the default mapping is used, which transforms data in the following csv or json format.

##### Assets data as a csv file

| Property        | Description                                        | Type   | Mandatory |
| :-------        | :----------                                        | :----  | :-------- |
| source_id_types | Tilde separated list of source id types            | string | yes       |
| source_ids      | Tilde separated list of source ids                 | string | yes       |
| offer_ids       | Tilde separated list of licence offer ids          | string | no        |
| set_ids         | Tilde separated list of set ids that it belongs to | string | no        |
| description     | Description of asset                               | string | no        |

##### Assets data as JSON

| Property    | Description                                | Type   | Mandatory |
| :-------    | :----------                                | :---   | :-------- |
| source_ids  | Array of source id objects                 | array  | yes       |
| offer_ids   | Array of licence offer ids                 | array  | no        |
| set_ids     | Array of set ids that the asset belongs to | array  | no        |
| description | Description of asset                       | string | no        |

###### Asset id object

| Property       | Description     | Type   |
| :-------       | :----------     | :---   |
| source_id_type | source id type  | string |
| source_id      | source id value | string |

#### Output
| Property | Description                           | Type   |
| :------- | :----------                           | :---   |
| status   | The status of the request             | number |
| data     | Successfully onboarded assets objects | array  |
| errors   | Errors returned during onboarding     | array  |

Errors will only be returned in response if errors were raised during onboarding.

##### Assets Object
| Property       | Description                               |
| :-------       | :----------                               |
| source_id_type | The type of the source id                 |
| source_id      | The source id                             |
| hub_id         | The hub id                                |
| same_as        | An array of alternative id type and value |

+ Request Onboard valid assets from csv (text/csv; charset=utf-8)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            source_id_types,source_ids,offer_ids,description
            examplecopictureid,100123,1~2~3~4,Sunset over a Caribbean beach
            examplecopictureid~anotherpictureid,100456~999002,1~2~3~4,Polar bear on an ice floe

+ Response 200 (application/json; charset=UTF-8)
    + Body

            {
                "status": 200,
                "data": [
                    {
                        "entity_id": "5d84d36d6eec446aae9c4435291eca8a",
                        "hub_key": "https://copyrighthub.org/s1/hub1/10e4b9612337f237118e1678ec001fa6/asset/5d84d36d6eec446aae9c4435291eca8a",
                        "entity_type": "asset",
                        "source_ids": [
                            {
                                "source_id": "100123",
                                "source_id_type": "examplecopictureid"
                            }
                        ]
                    },
                    {
                        "entity_id": "749ac740da53480d81f8568240e93fb2",
                        "hub_key": "https://copyrighthub.org/s1/hub1/10e4b9612337f237118e1678ec001fa6/asset/749ac740da53480d81f8568240e93fb2",
                        "entity_type": "asset",
                        "source_ids": [
                            {
                                "source_id": "100456",
                                "source_id_type": "examplecopictureid"
                            },
                            {
                                "source_id": "999002",
                                "source_id_type": "examplecopictureid"
                            }
                        ]
                    }
                ]
            }

+ Request Onboard valid assets from JSON (application/json; charset=utf-8)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            [
                {
                    "source_ids": [
                        {
                            "source_id_type": "examplecopictureid",
                            "source_id": "100123"
                        }
                    ],
                    "offer_ids": [
                        "1",
                        "2",
                        "3",
                        "4"
                    ],
                    "description": "Sunset over a Caribbean beach"
                },
                {
                    "source_ids": [
                        {
                            "source_id": "100456",
                            "source_id_type": "examplecopictureid"
                        },
                        {
                            "source_id_type": "anotherpictureid",
                            "source_id": "999002"
                        }
                    ],
                    "offer_ids": [
                        "1",
                        "2",
                        "3",
                        "4"
                    ],
                    "description": "Polar bear on an ice floe"
                }
            ]

+ Response 200 (application/json; charset=UTF-8)
    + Body

            {
                "status": 200,
                "data": [
                    {
                        "entity_id": "5d84d36d6eec446aae9c4435291eca8a",
                        "hub_key": "https://copyrighthub.org/s1/hub1/10e4b9612337f237118e1678ec001fa6/asset/5d84d36d6eec446aae9c4435291eca8a",
                        "entity_type": "asset",
                        "source_ids": [
                            {
                                "source_id_type": "examplecopictureid",
                                "source_id": "100123"
                            }
                        ]
                    },
                    {
                        "entity_id": "749ac740da53480d81f8568240e93fb2",
                        "hub_key": "https://copyrighthub.org/s1/hub1/10e4b9612337f237118e1678ec001fa6/asset/749ac740da53480d81f8568240e93fb2",
                        "entity_type": "asset",
                        "source_ids": [
                            {
                                "source_id": "100456",
                                "source_id_type": "examplecopictureid"
                            },
                            {
                                "source_id_type": "anotherpictureid",
                                "source_id": "999002"
                            }
                        ]
                    }
                ]
            }

+ Request Onboard assets with no data from csv  (text/csv; charset=utf-8)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body


+ Response 400 (application/json; charset=UTF-8)

    + Body

            {
                "status": 400,
                "errors": [
                    {
                        "source": "onboarding",
                        "line": 1,
                        "message": "Missing csv data"
                    }
                ]
            }
