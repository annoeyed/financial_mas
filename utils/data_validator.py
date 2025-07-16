from cerberus import Validator

schema = {
    'query': {'type': 'sting', 'minlength': 3}
    'params': {'type': 'dict'}
}
validator = Validator(schema)

def validate_request(data: dict) -> bool:
    return validator.validate(data)