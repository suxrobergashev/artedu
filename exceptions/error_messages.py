from rest_framework import status
from enum import Enum

class ErrorCodes(Enum):
    UNAUTHORIZED = 1
    INVALID_INPUT = 2
    NOT_FOUND = 3
    VALIDATION_FAILED = 4
    FORBIDDEN = 5
    ALREADY_EXISTS = 6
    USER_DOES_NOT_EXIST = 7
    INCORRECT_PASSWORD = 8

error_messages = {
    1: {"result": "Unauthorized access", "http_status": status.HTTP_401_UNAUTHORIZED},
    2: {"result": "Invalid input provided", "http_status": status.HTTP_400_BAD_REQUEST},
    3: {"result": "Resource not found", "http_status": status.HTTP_404_NOT_FOUND},
    4: {"result": "Validate Error", "http_status": status.HTTP_400_BAD_REQUEST},
    5: {"result": "Permission denied", "http_status": status.HTTP_403_FORBIDDEN},
    6: {"result": "User already exists", "http_status": status.HTTP_400_BAD_REQUEST},
    7: {"result": "User does not exist", "http_status": status.HTTP_400_BAD_REQUEST},
    8: {"result": "Incorrect password", "http_status": status.HTTP_400_BAD_REQUEST},
}


def get_error_message(code):
    return error_messages.get(code, 'Unknown error')