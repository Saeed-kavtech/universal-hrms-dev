from rest_framework.response import Response
from rest_framework import status


def successMsg():
    return ({'status': 200, 'system_status': '', 'data': '', 'message': '', 'system_error_message': ''})


def exception(e):
    api_response = successMsg()
    api_response['status'] = 400
    api_response['system_status'] = status.HTTP_400_BAD_REQUEST
    api_response['data'] = ''
    api_response['system_error_message'] = str(e)
    api_response['message'] = ''
    return Response(api_response)

def successMessage(msg):
    api_response = successMsg()
    api_response['status'] = 200
    api_response['system_status'] = status.HTTP_200_OK
    api_response['data'] = ''
    api_response['message'] = msg
    api_response['system_error_message'] = ''
    return Response(api_response)

def errorMessage(msg):
    api_response = successMsg()
    api_response['status'] = 400
    api_response['system_status'] = status.HTTP_400_BAD_REQUEST
    api_response['data'] = ''
    api_response['system_error_message'] = msg
    api_response['message'] = msg
    return Response(api_response,status=status.HTTP_400_BAD_REQUEST)

def errorMessageWithData(msg, data):
    api_response = successMsg()
    api_response['status'] = 400
    api_response['system_status'] = status.HTTP_400_BAD_REQUEST
    api_response['data'] = ''
    api_response['system_error_message'] = data
    api_response['message'] = msg
    return Response(api_response)

def nonexistent(var):
    api_response = successMsg()
    api_response['status'] = 400
    api_response['system_status'] = status.HTTP_404_NOT_FOUND
    api_response['data'] = ''
    api_response['system_error_message'] = ''
    api_response['message'] = f'This {var} does not exists in database'
    return Response(api_response)


def success(data):
    api_response = successMsg()
    api_response['status'] = 200
    api_response['system_status'] = status.HTTP_200_OK
    api_response['data'] = data
    api_response['message'] = 'Success'
    api_response['system_error_message'] = ''
    return Response(api_response)


def successfullyCreated(data):
    api_response = successMsg()
    api_response['status'] = 200
    api_response['system_status'] = status.HTTP_201_CREATED
    api_response['data'] = data
    api_response['message'] = 'Successfully Created'
    api_response['system_error_message'] = ''
    return Response(api_response)


def successfullyUpdated(data):
    api_response = successMsg()
    api_response['status'] = 200
    api_response['system_status'] = status.HTTP_200_OK
    api_response['data'] = data
    api_response['message'] = 'Updated Successfully'
    api_response['system_error_message'] = ''
    return Response(api_response)

def successMessageWithData(msg, data):
    api_response = successMsg()
    api_response['status'] = 200
    api_response['system_status'] = status.HTTP_200_OK
    api_response['data'] = data
    api_response['message'] = msg
    api_response['system_error_message'] = ''
    return Response(api_response)


def successfullyDeleted(data):
    api_response = successMsg()
    api_response['status'] = 200
    api_response['system_status'] = status.HTTP_200_OK
    api_response['data'] = data
    api_response['message'] = 'Deleted Successfully'
    api_response['system_error_message'] = ''
    return Response(api_response)


def serializerError(data):
    api_response = successMsg()
    api_response['status'] = 400
    api_response['system_status'] = status.HTTP_400_BAD_REQUEST
    api_response['data'] = ''
    api_response['message'] = 'Validation Error'
    api_response['system_error_message'] = data
    return Response(api_response)
