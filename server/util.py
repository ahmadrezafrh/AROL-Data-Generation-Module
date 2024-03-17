def validate(data: dict, type: str):
    if not data:
        return False, {'error': 'No data received'}

    if type == 'configuration':
        required_fields_conf = {
            'name': str,
            'machineriesSelected': list
        }
        for field, field_type in required_fields_conf.items():
            if field not in data or not isinstance(data[field], field_type):
                return False, {'error': f'The field {field} is required and must be of type {field_type.__name__}'}
    else:
        if len(data['machineriesSelected']) == 0 or not isinstance(data['machineriesSelected'], list):
            return False, {'error': 'At least one machinery is required'}


    required_fields_machinery= {
        'sensorsSelected': list,
        'uid': str,
        'modelName': str,
        "faultFrequency": int,
        'faultProbability': int
    }

    required_fields_sensor= {
        'name': str,
        'category': str,
        'dataFrequency': int,
        'heads': list
    }

    for machinery in data['machineriesSelected']:
        for field, field_type in required_fields_machinery.items():
            if field not in machinery or not isinstance(machinery[field], field_type):
                return False, {'error': f'The field {field} in each machinery is required and must be of type {field_type.__name__}'}
            if field == 'sensorsSelected' and len(machinery[field]) == 0:
                return False, {'error': f'At least one sensor has to be selected for each machinery'}
            if field == 'faultProbability' and (machinery[field] <= 0 or machinery[field] > 100):
                return False, {'error': 'The fault probability in each machinery must be greater than zero and less than or equal to one hundred'}
            if field == 'faultFrequency' and machinery[field] <= 0:
                return False, {'error': f'The fault frequency in each machinery must be greater then zero'}

        for sensor in machinery['sensorsSelected']:
            for field, field_type in required_fields_sensor.items():
                if field not in sensor or not isinstance(sensor[field], field_type):
                   return False, {'error': f'The field {field} in each sensor is required and must be of type {field_type.__name__}'}
                if field == 'heads' and len(sensor[field]) == 0:
                   return False, {'error': f'The list heads in each sensor must be not empty'}
                if field =='dataFrequency' and sensor[field] <= 0:
                   return False, {'error': f'The data frequency for each sensor must be greater then zero'}
                
            for head in sensor['heads']:
                if not isinstance(head, int):
                    return False, {'error': f'The elements in the sensor heads list must be of type int'}
    return True, None
