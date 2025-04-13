from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['total_pages'] = self.page.paginator.num_pages
        response.data['page_range'] = list(self.page.paginator.page_range)
        response.data['current_page'] = self.page.number
        return response