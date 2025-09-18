from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard paginator with default page size.
    Allows client override via ?page_size=...
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


def paginate_queryset(queryset, request, serializer_func):
    """
    Helper to paginate any queryset or list.
    serializer_func: function to serialize each object.
    """
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        return paginator.get_paginated_response([serializer_func(obj) for obj in page])
    return Response([serializer_func(obj) for obj in queryset])
