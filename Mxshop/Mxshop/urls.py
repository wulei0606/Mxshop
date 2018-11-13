"""Mxshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.urls import include
import xadmin
from Mxshop.settings import MEDIA_ROOT
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from goods.views import GoodsListViewSet,CategoryViewset

router = DefaultRouter()
#配置goods的url
router.register('goods',GoodsListViewSet, base_name="goods")
#配置category的url
router.register('categorys',CategoryViewset, base_name="categorys")


# goods_list = GoodsListViewSet.as_view({
#     'get':'list',
# })

urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    path('ueditor/',include('DjangoUeditor.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('media/<path:path>',serve,{'document_root':MEDIA_ROOT}),

    path('',include(router.urls)),

    path('docs/',include_docs_urls(title="生鲜商城")),

    # drf自带的token认证模式
    path('api-token-auth/', views.obtain_auth_token),
]
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )