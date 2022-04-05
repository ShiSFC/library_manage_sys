"""TuShuGuan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path, include
from app01.views import *

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('regist/', register),  # 图书馆注册页面
    path('login/', login, name='login'),  # 图书馆登录页面
    path('check_pwd/', login_check, name='check_pwd'),   # 检查密码
    path('logout/', logout, name='logout'),
    path('index/', index, name='index'),   # 首页
    path('index/query/', index_query, name='index_query'),   # 首页查询
    path('set_password/', set_password),  # 图书馆重置密码页面
    path('ul/', include('app01.urls')),
]
