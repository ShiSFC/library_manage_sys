from django.conf.urls import url
from django.urls import path

from app01.views import *

urlpatterns = [
    path('menu/book/', book, name='book_show'),
    path('menu/book/add/', book_add, name='book_add'),
    path('menu/book/edit/', book_edit, name='book_edit'),
    path('menu/book/del/', book_del, name='book_del'),
    path('menu/book/detail/', book_detail, name='book_detail'),
    path('menu/query/book', book_query, name='book_query'),
    path('menu/book/borrow/', book_borrow, name='book_borrow'),

    path('menu/borrowingLog/', borrowingLog, name='borrowingLog_show'),  # 操作日志
    path('menu/borrowingLog/edit/', borrowingLog_edit, name='borrowingLog_edit'),
    path('menu/borrowingLog/del/', borrowingLog_del, name='borrowingLog_del'),
    path('menu/borrowingLog/return/', borrowingLog_return, name='borrowingLog_return'),

    path('menu/author/', author, name='author_show'),  # 作者
    path('menu/author/add/', author_add, name='author_add'),
    path('menu/author/edit/', author_edit, name='author_edit'),
    path('menu/author/del/', author_del, name='author_del'),

    path('menu/publish/', publish, name='publish_show'),  # 出版社
    path('menu/publish/add/', publish_add, name='publish_add'),
    path('menu/publish/edit/', publish_edit, name='publish_edit'),
    path('menu/publish/del/', publish_del, name='publish_del'),


    path('menu/reader/', reader, name='reader_show'),
    path('menu/reader/add/', reader_add, name='reader_add'),
    path('menu/reader/edit/', reader_edit, name='reader_edit'),
    path('menu/reader/del/', reader_del, name='reader_del'),

]
