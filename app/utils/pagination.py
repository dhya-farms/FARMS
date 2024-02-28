from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        # Check if 'page' query parameter is set to 'all'
        if request.query_params.get('page', '').lower() == 'all':
            # Indicate that all items should be returned
            self.return_all = True
            return list(queryset)  # Return a list to bypass further pagination processing
        else:
            self.return_all = False  # Normal pagination path
            return super().paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        # If all items are being returned, don't include pagination details
        if getattr(self, 'return_all', False):
            return Response(OrderedDict([
                ('count', 1000),
                ('next', ''),
                ('previous', ''),
                ('page_size', self.page_size),
                ('results', data)
            ]))
        else:
            # Normal paginated response
            return super().get_paginated_response(data)
