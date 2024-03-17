# AROL-CLOUD (SDP Projects 2023-2024 Proposal 2 - Data Generation)

This project builds upon the original work by Mario Deda. The primary addition is a new feature called "Data Generation." This feature enables users to define a template, from which synthetic data for chosen sensors and machineries will be generated.

## How to run project locally

### Important note

To run the project locally, it is essential that MongoDB is properly installed on your system. Furthermore, it is crucial to configure MongoDB to listen on the specific host and port configuration:

```
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

### Run server

Step 1: ```cd ./python-server```

Step 2: ```pip install -r requirements.txt```

Step 3: ```python server.py```

### Run client

Step 1: ```cd ./react-client```

Step 2: ```npm install --force```

Step 3: ```npm run start```

## How to run project with Docker

Step 1: ```Make sure you have Docker installed locally on your system```

Step 2: ```cd ./Docker```

Step 3: ```docker compose up --build```

Step 4: ```Open Docker Desktop and make sure to run all the containers under the "arol-cloud_data_generation" container```

Step 5: ```Open http://localhost:3000 on your favourite browser```

## API Documentation

Base URLs:

* <a href="http://localhost:5000">http://localhost:5000</a>

## post__generate_configuration

`POST /generate/configuration`

*Insert a configuration*

Insert a new configuration

> Body parameter

```json
{
  "name": "string",
  "machineriesSelected": [
    {
      "uid": "string",
      "modelName": "string",
      "faultFrequency": 0,
      "faultProbability": 0,
      "sensorsSelected": [
        {
          "name": "string",
          "category": "string", 
          "heads": [0],
          "dataFrequency": 0
        }
      ]
    }
  ]
}
```

<h3 id="post__generate_configuration-parameters">Parameters</h3>

| Name                  | In   | Type                                         | Required | Description        |
| --------------------- | ---- | -------------------------------------------- | -------- | ------------------ |
| body                  | body | [Configuration](#schemaConfiguration)        | true     | Configuration data |
| » name                | body | string                                       | true     | none               |
| » machineriesSelected | body | [MachinerySelected](schemaMachinerySelected) | true     | none               |
| »» uid                | body | string                                       | true     | none               |
| »» modelName          | body | string                                       | true     | none               |
| »» faultFrequency     | body | number                                       | true     | none               |
| »» faultProbability   | body | number                                       | true     | none               |
| »» sensorsSelected    | body | [SensorSelected](schemaSensorSelected)       | true     | none               |
| »»» name              | body | string                                       | true     | none               |
| »»» category          | body | string                                       | true     | none               |
| »»» heads             | body | [number]                                     | true     | none               |
| »»» dataFrequency     | body | number                                       | true     | none               |


<h3 id="post__generate_configuration-responses">Responses</h3>

| Status | Meaning                                                                    | Description                                  | Schema                                                |
| ------ | -------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                    | Configuration inserted                       | [ConfigurationResponse](#schemaConfigurationResponse) |
| 400    | [Bad Request](https://tools.ietf.org/html/rfc7235#section-6.5.1)           | Invalid configuration detected               | None                                                  |
| 500    | [Internal Server Error](https://tools.ietf.org/html/rfc7235#section-6.6.1) | Server encountered an unexpected contidition | None                                                  |

> Example responses

> 200 Response

```json
{
  "message": "Configuration saved",
  "configuration": {
    "_id": 0,
    "name": "string",
    "machineriesSelected": [
      {
        "uid": "string",
        "modelName": "string",
        "faultFrequency": 0,
        "faultProbability": 0,
        "sensorsSelected": [
          {
            "name": "string",
            "category": "string", 
            "heads": [0],
            "dataFrequency": 0
          }
        ]
      }
    ]
  }
}
```

> 400 Response

```json
{ 
  "error": "The field name is required and must be of type str"
}
```

> 500 Response

```json
{ 
  "error": "Internal server error"
}
```

## put__generate_configuration_{name}

`PUT /generate/configuration/{name}`

*Update a configuration*

Update a saved configuration whose name is given

> Body parameter

```json
{
  "machineriesSelected": [
    {
      "uid": "string",
      "modelName": "string",
      "faultFrequency": 0,
      "faultProbability": 0,
      "sensorsSelected": [
        {
          "name": "string",
          "category": "string", 
          "heads": [0],
          "dataFrequency": 0
        }
      ]
    }
  ]
}
```

<h3 id="put__generate_configuration_{name}-parameters">Parameters</h3>

| Name                  | In   | Type                                                            | Required | Description        |
| --------------------- | ---- | --------------------------------------------------------------- | -------- | ------------------ |
| name                  | path | string                                                          | true     | Configuration name |
| body                  | body | [MachinerySelectedResponse](#schemaMachineriesSelectedResponse) | true     | none               |
| » machineriesSelected | body | [MachinerySelected](schemaMachinerySelected)                    | true     | none               |
| »» uid                | body | string                                                          | true     | none               |
| »» modelName          | body | string                                                          | true     | none               |
| »» faultFrequency     | body | number                                                          | true     | none               |
| »» faultProbability   | body | number                                                          | true     | none               |
| »» sensorsSelected    | body | [SensorSelected](schemaSensorSelected)                          | true     | none               |
| »»» name              | body | string                                                          | true     | none               |
| »»» category          | body | string                                                          | true     | none               |
| »»» heads             | body | [number]                                                        | true     | none               |
| »»» dataFrequency     | body | number                                                          | true     | none               |


<h3 id="put__generate_configuration_{name}-responses">Responses</h3>

| Status | Meaning                                                                    | Description                                  | Schema                                                |
| ------ | -------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                    | Configuration updated                        | [ConfigurationResponse](#schemaConfigurationResponse) |
| 204    | [No Content](https://tools.ietf.org/html/rfc7231#section-6.3.5)            | Nothing to update                            | None                                                  |
| 400    | [Bad Request](https://tools.ietf.org/html/rfc7235#section-6.5.1)           | Invalid configuration detected               | None                                                  |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)             | Configuration with the given name not found  | None                                                  |
| 500    | [Internal Server Error](https://tools.ietf.org/html/rfc7235#section-6.6.1) | Server encountered an unexpected contidition | None                                                  |

> Example responses

> 200 Response

```json
{
  "message": "Update saved",
  "configuration": {
    "_id": 0,
    "name": "string",
    "machineriesSelected": [
      {
        "uid": "string",
        "modelName": "string",
        "faultFrequency": 0,
        "faultProbability": 0,
        "sensorsSelected": [
          {
            "name": "string",
            "category": "string", 
            "heads": [0],
            "dataFrequency": 0
          }
        ]
      }
    ]
  }
}
```
> 204 Response

```json
{ 
  "message": "No changes to save"
}
```

> 400 Response

```json
{ 
  "error": "At least one machinery is required"
}
```

> 404 Response

```json
{ 
  "error": "Configuration not found"
}
```

> 500 Response

```json
{ 
  "error": "Internal server error"
}
```

## get__generate_configurations_{name}

`GET /generate/configurations/{name}`

*Configuration by its name*

Get a saved configuration by its name

<h3 id="get__generate_configurations_{name}-parameters">Parameters</h3>

| Name | In   | Type   | Required | Description                           |
| ---- | ---- | ------ | -------- | ------------------------------------- |
| name | path | string | true     | The name of the desired configuration |


<h3 id="get__generate_configurations_{name}-responses">Responses</h3>

| Status | Meaning                                                                    | Description                                  | Schema                                                |
| ------ | -------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                    | Configuration information                    | [ConfigurationResponse](#schemaConfigurationResponse) |
| 400    | [Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)           | Invalid configuration name detected          | None                                                  |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)             | Configuration with the given name not found  | None                                                  |
| 500    | [Internal Server Error](https://tools.ietf.org/html/rfc7235#section-6.6.1) | Server encountered an unexpected contidition | None                                                  |

> Example responses

> 200 Response

```json
{
  "message": "Configuration retrievd with success",
  "configuration": {
    "_id": 0,
    "name": "string",
    "machineriesSelected": [
      {
        "uid": "string",
        "modelName": "string",
        "faultFrequency": 0,
        "faultProbability": 0,
        "sensorsSelected": [
          {
            "name": "string",
            "category": "string", 
            "heads": [0],
            "dataFrequency": 0
          }
        ]
      }
    ]
  }
}
```
> 400 Response

```json
{ 
  "error": "The name parameter must be provided as a valid string"
}
```

> 404 Response

```json
{ 
  "error": "Configuration not found"
}
```

> 500 Response

```json
{ 
  "error": "Internal server error"
}
```

## get__generate_configuraion_names

`GET /generate/configuration/names`

*Configuration Names*

Get the names of the configurations saved

<h3 id="get__generate_ConfigurationsNames-responses">Responses</h3>

| Status | Meaning                                                                    | Description                                  | Schema                                            |
| ------ | -------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                    | Configuration names                          | [ConfigurationsNames](#schemaConfigurationsNames) |
| 500    | [Internal Server Error](https://tools.ietf.org/html/rfc7235#section-6.6.1) | Server encountered an unexpected contidition | None                                              |

> Example responses

> 200 Response

```json
{
  "configurationsNames":  [
    "string"
  ]
}
```

> 500 Response

```json
{ 
  "error": "Internal server error"
}
```

## delete__generate_configuration_{name}

`DELETE /generate/configuration/{name}`

*Delete configuration*

Delete a configuration by its name

<h3 id="delete__generate_configuration_{name}-parameters">Parameters</h3>

| Name | In   | Type   | Required | Description                           |
| ---- | ---- | ------ | -------- | ------------------------------------- |
| name | path | string | true     | The name of the desired configuration |


<h3 id="delete__generate_configuration_{name}-responses">Responses</h3>

| Status | Meaning                                                                    | Description                                  | Schema |
| ------ | -------------------------------------------------------------------------- | -------------------------------------------- | ------ |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                    | Configuration deleted successfully           | None   |
| 400    | [Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)           | Invalid configuration name detected          | None   |
| 404    | [Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)             | Configuration with the given name not found  | None   |
| 500    | [Internal Server Error](https://tools.ietf.org/html/rfc7235#section-6.6.1) | Server encountered an unexpected contidition | None   |

> Example responses

> 200 Response

```json
{
  "message": "Configuration deleted"
}
```

> 400 Response

```json
{ 
  "error": "The name parameter must be provided as a valid string"
}
```

> 404 Response

```json
{ 
  "error": "Configuration not found"
}
```

> 500 Response

```json
{ 
  "error": "Internal server error"
}
```
## get__model_status

`GET /generate/model/status`

*Model status*

Check if there is a model aldready trained or not

<h3 id="put__generate_model_status-responses">Responses</h3>

| Status | Meaning                                                                    | Description                                  | Schema |
| ------ | -------------------------------------------------------------------------- | -------------------------------------------- | ------ |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                    | Status of the model obtained                 | None   |
| 500    | [Internal Server Error](https://tools.ietf.org/html/rfc7235#section-6.6.1) | Server encountered an unexpected contidition | None   |

> Example responses

> 200 Response

```json
{
  "message": "Model already trained",
  "trained": true
}
```

> 500 Response

```json
{ 
  "error": "Internal server error"
}
```

## put__model_train

`PUT /generate/model/train`

*Train model*

Train the model

<h3 id="put__generate_model_train-responses">Responses</h3>

| Status | Meaning                                                                    | Description                                  | Schema |
| ------ | -------------------------------------------------------------------------- | -------------------------------------------- | ------ |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                    | Model trained successfully                   | None   |
| 500    | [Internal Server Error](https://tools.ietf.org/html/rfc7235#section-6.6.1) | Server encountered an unexpected contidition | None   |

> Example responses

> 200 Response

```json
{
  "message": "Model trained"
}
```

> 500 Response

```json
{ 
  "error": "Internal server error"
}
```


## post_simulation_run

`POST /generate/simulation/run`

*Run Simulation*

Run a simulation and saved each generated data

> Body parameter

```json
{
  "machineriesSelected": [
    {
      "uid": "string",
      "modelName": "string",
      "faultFrequency": 0,
      "faultProbability": 0,
      "sensorsSelected": [
        {
          "name": "string",
          "category": "string", 
          "heads": [0],
          "dataFrequency": 0
        }
      ]
    }
  ]
}
```

<h3 id="post__generate_simualtion_run-parameters">Parameters</h3>

| Name                  | In   | Type                                                          | Required | Description               |
| --------------------- | ---- | ------------------------------------------------------------- | -------- | ------------------------- |
| body                  | body | [MachinerySelectedResponse](#schemaMachinerySelectedResponse) | true     | Machineries selected data |
| » machineriesSelected | body | list                                                          | true     | none                      |
| »» uid                | body | string                                                        | true     | none                      |
| »» modelName          | body | string                                                        | true     | none                      |
| »» faultFrequency     | body | number                                                        | true     | none                      |
| »» faultProbability   | body | number                                                        | true     | none                      |
| »» sensorsSelected    | body | list                                                          | true     | none                      |
| »»» name              | body | string                                                        | true     | none                      |
| »»» category          | body | string                                                        | true     | none                      |
| »»» heads             | body | [number]                                                      | true     | none                      |
| »»» dataFrequency     | body | number                                                        | true     | none                      |

<h3 id="post__generate_simualtion_run-responses">Responses</h3>

| Status | Meaning                                                                    | Description                                  | Schema                                    |
| ------ | -------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------- |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                    | Simulation completed                         | [SimulationStats](#schemaSimulationStats) |
| 400    | [Bad Request](https://tools.ietf.org/html/rfc7235#section-6.5.1)           | Invalid configuration detected               | None                                      |
| 500    | [Internal Server Error](https://tools.ietf.org/html/rfc7235#section-6.6.1) | Server encountered an unexpected contidition | None                                      |


> Example responses

> 200 Response

```json
{
  "message": "The data have been generated",
  "samples_generated": 0,
  "faults_generated": 0,
  "simulation_time": 0
}
```

> 400 Response

```json
{ 
  "error": "At least one machinery is required"
}
```

> 404 Response

```json
{ 
  "error": "Configuration not found"
}
```

> 500 Response

```json
{ 
  "error": "Internal server error"
}
```

## put__simulation_stop

`PUT /generate/simulation/stop`

*Stop simulation*

Stop a running simulation

<h3 id="put__generate_simulation_stop-responses">Responses</h3>

| Status | Meaning                                                                    | Description                                  | Schema |
| ------ | -------------------------------------------------------------------------- | -------------------------------------------- | ------ |
| 200    | [OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)                    | Simulation stopped successfully              | None   |
| 204    | [No Content](https://tools.ietf.org/html/rfc7231#section-6.3.5)            | No simulation to stop                        | None   |
| 500    | [Internal Server Error](https://tools.ietf.org/html/rfc7235#section-6.6.1) | Server encountered an unexpected contidition | None   |

> Example responses

> 200 Response

```json
{
  "message": "Simulation stopped"
}
```

> 204 Response

```json
{
  "message": "No action to interrumpt"
}
```

> 500 Response

```json
{ 
  "error": "Internal server error"
}
```


# Schemas

<h2 id="schemaConfiguration">Configuration</h2>
<a id="schemaConfiguration"></a>

```json
{
  "name": "string",
  "machineriesSelected": [
    {
      "uid": "string",
      "modelName": "string",
      "faultFrequency": 0,
      "faultProbability": 0,
      "sensorsSelected": [
        {
          "name": "string",
          "category": "string", 
          "heads": [0],
          "dataFrequency": 0
        }
      ]
    }
  ]
}
```

### Properties

| Name                | Type                | Required | Restrictions   | Description |
| ------------------- | ------------------- | -------- | -------------- | ----------- |
| name                | string              | true     | none           | none        |
| machineriesSelected | [MachinerySelected] | true     | none           | none        |
| » uid               | string              | true     | none           | none        |
| » modelName         | string              | true     | none           | none        |
| » faultFrequency    | number              | true     | none           | none        |
| » faultProbability  | number              | true     | >= 0 && <= 100 | none        |
| » sensorsSelected   | [SensorSelected]    | true     | none           | none        |
| »» name             | string              | true     | none           | none        |
| »» category         | string              | true     | none           | none        |
| »» heads            | [number]            | true     | none           | none        |
| »» dataFrequency    | number              | true     | none           | none        |

<h2 id="schemaMachinerySelected">MachinerySelected</h2>
<a id="schemaMachinerySelected"></a>

```json
{
  "uid": "string",
  "modelName": "string",
  "faultFrequency": 0,
  "faultProbability": 0,
  "sensorsSelected": [
    {
      "name": "string",
      "category": "string", 
      "heads": [0],
      "dataFrequency": 0
    }
  ]
}
```

### Properties

| Name             | Type             | Required | Restrictions   | Description |
| ---------------- | ---------------- | -------- | -------------- | ----------- |
| uid              | string           | true     | none           | none        |
| modelName        | string           | true     | none           | none        |
| faultFrequency   | number           | true     | none           | none        |
| faultProbability | number           | true     | >= 0 && <= 100 | none        |
| sensorsSelected  | [SensorSelected] | true     | none           | none        |
| » name           | string           | true     | none           | none        |
| » category       | string           | true     | none           | none        |
| » heads          | [number]         | true     | none           | none        |
| » dataFrequency  | number           | true     | none           | none        |

<h2 id="schemaSensorSelected">SensorSelected</h2>
<a id="schemaSensorSelected"></a>

```json
{
  "name": "string",
  "category": "string", 
  "heads": [0],
  "dataFrequency": 0
}

```

### Properties

| Name          | Type     | Required | Restrictions | Description |
| ------------- | -------- | -------- | ------------ | ----------- |
| name          | string   | true     | none         | none        |
| category      | string   | true     | none         | none        |
| heads         | [number] | true     | none         | none        |
| dataFrequency | number   | true     | none         | none        |


<h2 id="schemaMachinerySelectedResponse">MachinerySelectedResponse</h2>
<a id="schemaMachinerySelectedResponse"></a>

```json
{
  "machineriesSelected": [
    {
      "uid": "string",
      "modelName": "string",
      "faultFrequency": 0,
      "faultProbability": 0,
      "sensorsSelected": [
        {
          "name": "string",
          "category": "string", 
          "heads": [0],
          "dataFrequency": 0
        }
      ]
    }
  ]
}
```

### Properties

| Name                | Type                | Required | Restrictions   | Description |
| ------------------- | ------------------- | -------- | -------------- | ----------- |
| machineriesSelected | [MachinerySelected] | true     | none           | none        |
| uid                 | string              | true     | none           | none        |
| modelName           | string              | true     | none           | none        |
| faultFrequency      | number              | true     | none           | none        |
| faultProbability    | number              | true     | >= 0 && <= 100 | none        |
| sensorsSelected     | [SensorSelected]    | true     | none           | none        |
| » name              | string              | true     | none           | none        |
| » category          | string              | true     | none           | none        |
| » heads             | [number]            | true     | none           | none        |
| » dataFrequency     | number              | true     | none           | none        |


<h2 id="schemaConfigurationResponse">ConfigurationResponse</h2>
<a id="schemaConfigurationResponse"></a>

```json
{
  "message": "Configuration saved",
  "configuration": {
    "_id": 0,
    "name": "string",
    "machineriesSelected": [
      {
        "uid": "string",
        "modelName": "string",
        "faultFrequency": 0,
        "faultProbability": 0,
        "sensorsSelected": [
          {
            "name": "string",
            "category": "string", 
            "heads": [0],
            "dataFrequency": 0
          }
        ]
      }
    ]
  }
}
```

### Properties

| Name                  | Type                | Required | Restrictions   | Description |
| --------------------- | ------------------- | -------- | -------------- | ----------- |
| message               | string              | true     | none           | none        |
| Configuration         | object              | true     | none           | none        |
| » id                  | string              | true     | none           | none        |
| » name                | string              | true     | none           | none        |
| » machineriesSelected | [MachinerySelected] | true     | none           | none        |
| »» uid                | string              | true     | none           | none        |
| »» modelName          | string              | true     | none           | none        |
| »» faultFrequency     | number              | true     | none           | none        |
| »» faultProbability   | number              | true     | >= 0 && <= 100 | none        |
| »» sensorsSelected    | [SensorSelected]    | true     | none           | none        |
| »»» name              | string              | true     | none           | none        |
| »»» category          | string              | true     | none           | none        |
| »»» heads             | [number]            | true     | none           | none        |
| »»» dataFrequency     | number              | true     | none           | none        |

<h2 id="schemaConfigurationsNames">ConfigurationsNames</h2>
<a id="schemaConfigurationsNames"></a>

```json
{
  "configurationsNames":  [
    "string"
  ]
}
```

### Properties

| Name                | Type     | Required | Restrictions | Description |
| ------------------- | -------- | -------- | ------------ | ----------- |
| configurationsNames | [string] | true     | none         | none        |

<h2 id="schemaSimulationStats">SimulationStats</h2>
<a id="schemaSimulationStats"></a>

```json
{
  "message": "The data have been generated",
  "samples_generated": 0,
  "faults_generated": 0,
  "simulation_time": 0
}
```

### Properties

| Name              | Type   | Required | Restrictions | Description |
| ----------------- | ------ | -------- | ------------ | ----------- |
| message           | string | true     | none         | none        |
| samples_generated | number | true     | none         | none        |
| faults_generated  | number | true     | none         | none        |
| simulation_time   | number | true     | none         | none        |