from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from travel.services import ServiceUnavailableError


def custom_exception_handler(exc, context):
    if isinstance(exc, ServiceUnavailableError):
        return Response({'detail': exc.message}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return drf_exception_handler(exc, context)
