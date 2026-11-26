from rest_framework.pagination import PageNumberPagination


# 32.1 создаем класс пагинации для постраничного вывода списка курсов и уроков
class MaterialsPagination(PageNumberPagination):
    # 32.1 задаем количество элементов на одной странице по умолчанию
    page_size = 5
    # 32.1 указываем имя query-параметра для динамического изменения размера страницы в запросе
    page_size_query_param = 'page_size'
    # 32.1 ограничиваем максимально допустимое количество элементов на одной странице
    max_page_size = 50
