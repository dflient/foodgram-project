from rest_framework.pagination import PageNumberPagination

from foodgram_backend.constants import MAX_PAGE_SIZE_LENGHT


class RecipePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE_LENGHT
