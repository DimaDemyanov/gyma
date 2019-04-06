from collections import OrderedDict
import json

from gyma.vdv.app import SWAGGER_SPEC_PATH, baseURL


def get_swagger_spec(swagger_spec_path=SWAGGER_SPEC_PATH):
    try:
        with open(SWAGGER_SPEC_PATH) as f:
            swagger_spec = json.loads(f.read(), object_pairs_hook=OrderedDict)
    except FileNotFoundError:
        raise Exception("Unable to parse the Swagger spec JSON document.")
    return swagger_spec


def get_uri_path_by_opearation_id(operation_id, swagger_spec_path=SWAGGER_SPEC_PATH):
    swagger_spec = get_swagger_spec(swagger_spec_path)

    for path in swagger_spec['paths'].keys():
        for http_method in swagger_spec['paths'][path].keys():
            if swagger_spec['paths'][path][http_method]['operationId'] == operation_id:
                return '{base_url}{path}'.format(base_url=baseURL, path=path)


# MARK: - Not in use:

def get_uri_parameters_in_path(path, swagger_spec_path=SWAGGER_SPEC_PATH):
    swagger_spec = get_swagger_spec(swagger_spec_path)

    for k in swagger_spec['paths'].keys():
        for http_method in swagger_spec['paths'][k].keys():
            http_method_description = swagger_spec['paths'][k][http_method]
            if http_method_description['operationId'] == operationId:
                parameters = http_method_description['parameters']
                for parameter in parameters:
                    if parameter['in'] != 'path':
                        pass
                        # not return
                    else:
                        pass
                        # return


# MARK: - Not in use:

def get_paramater_enum(parameter):
    try:
        parameter_enum = param['enum']
    except KeyError:
        return None
    return parameter
