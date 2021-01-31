from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_409_CONFLICT

def custom_exception_handler(exc, context):
    # take all response errors from list
    response = exception_handler(exc, context)
    if not response:
        return response
    for error in response.data:
        if isinstance(response.data[error], list):
            response.data[error] = response.data[error][0]
    return response


class UsernameAlreadyExistsError(APIException):
    status_code = HTTP_409_CONFLICT
    default_detail = 'Username already exists'

