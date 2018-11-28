import django_filters
from django.db.models import Q

from .models import Goods

class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    商品的过滤类
    """
    pricemin = django_filters.NumberFilter(field_name="shop_price",lookup_expr='gte')
    pricemax = django_filters.NumberFilter(field_name="shop_price",lookup_expr='lte')
    #模糊查询
    name = django_filters.CharFilter(field_name="name",lookup_expr='icontains')
    top_category = django_filters.NumberFilter(field_name="category", method='top_category_filter')

    def top_category_filter(self, queryset, name, value):
        # 不管当前点击的是一级目录二级目录还是三级目录。
        return queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(
            category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ["pricemin","pricemax",'name']