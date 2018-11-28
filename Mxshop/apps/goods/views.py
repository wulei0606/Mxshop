from django.shortcuts import render
from .serializers import GoodsSerializer, BannerSerializer, IndexCategorySerializer, HotWordsSerializer

# Create your views here.

from rest_framework import mixins
from rest_framework import generics

from rest_framework import filters

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


from .models import Goods, Banner, HotSearchWords

from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from .models import Goods, GoodsCategory, GoodsImage, GoodsCategoryBrand
from .serializers import GoodsSerializer, CategorySerializer
from .filters import GoodsFilter



class GoodsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


# class GoodsListView(APIView):
#     """
#     商品列表
#     """
#     def get(self,request,format=None):
#         goods = Goods.objects.all()[:10]
#         goods_serializer = GoodsSerializer(goods,many=True)
#         return Response(goods_serializer.data)
#
#     def post(self,request,format=None):
#         serilizer = GoodsSerializer(data=request.data)
#         if serilizer.is_valid():
#             serilizer.save()
#             return Response(serilizer.data,status=status.HTTP_201_CREATED)
#         return Response(serilizer.errors,status=status.HTTP_400_BAD_REQUEST)
# class GoodsListView(generics.ListAPIView):
#     """
#     商品列表页
#     """
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#     pagination_class = GoodsPagination


# class GoodsListViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#     pagination_class = GoodsPagination

class GoodsListViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表页
    """
    queryset = Goods.objects.get_queryset().order_by('id')
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    # authentication_classes = (TokenAuthentication,)
    # 过滤
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = GoodsFilter
    # 搜索
    search_fields = ("name", 'goods_brief', 'goods_desc')
    # 排序
    ordering_fields = ('sold_num', 'add_time')
    # #自定义过滤字段
    # def get_queryset(self):
    #     #queryset = Goods.objects.all()
    #     price_min = self.request.query_params.get("price_min",0)
    #     if price_min:
    #         self.queryset = Goods.objects.filter(shop_price__gt=int(price_min)).order_by('-add_time')
    #     return self.queryset


class CategoryViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品分类列表数据
    retrieve:
        获取商品分类详情
    """
    queryset = GoodsCategory.objects.get_queryset().filter(category_type=1)
    # queryset = GoodsCategory.objects.all()
    serializer_class = CategorySerializer

class BannerViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取轮播图列表
    """
    queryset = Banner.objects.get_queryset().order_by("index")
    serializer_class = BannerSerializer


class IndexCategoryViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页商品分类数据
    """
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=["生鲜食品", "酒水饮料"])
    serializer_class = IndexCategorySerializer


class HotSearchsViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取热搜词列表
    """
    queryset = HotSearchWords.objects.get_queryset().order_by("-index")
    serializer_class = HotWordsSerializer