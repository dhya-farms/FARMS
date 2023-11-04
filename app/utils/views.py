from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from app.utils.authentication import IsOrganizationUser
from app.utils.helpers import get_data_for_field


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsOrganizationUser])
def get_enum_values(request):
    # TODO Not the best way. Think for a better solution.

    """
        Serves GET requests given on the entity API root path which provide all enums values
        GET /api/get-enum-values
        :param request:
        :return:
    """

    locale = request.LANGUAGE_CODE
    fields = ('WeightUnit',
              'RecordType',
              'PayType',
              'PlaceType',
              'Designation',
              )
    data = {}
    for field in fields:
        data[field] = get_data_for_field(field=field, locale=locale)
    return JsonResponse(data=data, status=status.HTTP_200_OK)
