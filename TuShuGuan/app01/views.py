import datetime
import re

from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib import auth
from django.utils import timezone

from app01 import models
from app01.models import Regist, Log_in


# 注册
def register(request):
    if request.method == 'GET':
        obj = Regist()
        return render(request, 'register.html', {'obj': obj})
    else:
        obj = Regist(request.POST)
        # print("obj:"+request.POST.toString())
        flag = obj.is_valid()  # 验证数据
        data = obj.cleaned_data  # 规范化数据
        # 验证用户名是否已存在
        user = User.objects.filter(username__exact=data.get('username'))
        # user = auth.authenticate(username=data.get('username'))  # 找不到数据时会报错
        if user:
            obj.error_message = '用户名已存在'
        elif flag:
            User.objects.create_user(**data)
            return redirect('/login')
        return render(request, 'register.html', {'obj': obj})


# 登录
def login(request):
    if request.method == 'GET':
        obj = Log_in()
        return render(request, 'login.html', {'obj': obj})
    else:
        obj = Log_in(request.POST)
        if obj.is_valid():
            data = obj.cleaned_data
            user = auth.authenticate(username=data.get('user'),
                                     password=data.get('pwd'))
            if user:
                auth.login(request, user)
                return redirect('/ul/menu/book/')
            else:
                obj.error_message = '用户名或密码错误'
                return render(request, 'login.html', {'obj': obj})
        else:
            return render(request, 'login.html', {'obj': obj})


# 重置密码
def set_password(request):
    if request.method == 'GET':
        return render(request, 'set_password.html')
    else:
        oldpwd = request.POST.get('oldpwd')
        newpwd = request.POST.get('newpwd')
        user = request.user
        if user.check_password(oldpwd):
            user.set_password(newpwd)
            user.save()
            return redirect('/login/')
        else:
            return render(request, 'set_password.html')


# 书籍信息
def book(request):
    page_number = request.GET.get("page")
    books = models.Book.objects.all()
    p = Paginator(books, 8)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_book.html', locals())


# 作者信息
def author(request):
    page_number = request.GET.get("page")
    book_lists = models.Author.objects.all()
    p = Paginator(book_lists, 8)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_author.html', locals())


# 出版社信息
def publish(request):
    page_number = request.GET.get("page")
    book_lists = models.Publish.objects.all()
    p = Paginator(book_lists, 8)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_publish.html', locals())


# 读者信息
def reader(request):
    page_number = request.GET.get("page")
    readers = models.Reader.objects.all() #.order_by('certificate')
    p = Paginator(readers, 8)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_reader.html', locals())


# 借阅管理日志信息
def borrowingLog(request):
    page_number = request.GET.get("page")
    book_lists = models.BorrowingLog.objects.all()
    p = Paginator(book_lists, 10)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_borrowingLog.html', locals())


# 添加书籍
def book_add(request):
    if request.method == 'GET':
        obj = {}
        obj["enterDate"] = datetime.date.today()
        authors = models.Author.objects.all()
        publishs = models.Publish.objects.all()
        return render(request, 'menu_book_add.html', locals())
    else:
        obj = request.POST.dict()
        print(obj)
        if("author_id" in obj):
            obj.pop("author_id")
        book = models.Book.objects.create(**obj)
        flag = book.save()
        author_id = request.POST.getlist('author_id')
        authors_list = models.Author.objects.filter(id__in=author_id)
        if len(author_id) != 0 and not flag:
            book.author.add(*authors_list)
            flag = book.save()
            return redirect('/ul/menu/book/')

        obj["author_error"] = "作者不能为空"
        author_list = []
        for author in authors_list:
            author_list.append(author.id)
        authors = models.Author.objects.all()
        publishs = models.Publish.objects.all()
        obj['error'] = flag
        obj["publish_id"] = int(obj["publish_id"])
        obj["publishDate"] = datetime.datetime.strptime(obj["publishDate"], '%Y-%m-%d')
        obj["enterDate"] = datetime.datetime.strptime(obj["enterDate"], '%Y-%m-%d')
        print(obj)
        return render(request, 'menu_book_add.html', locals())


# 添加作者
def author_add(request):
    name = request.POST.get("name").strip(' ')
    sex = request.POST.get("sex")
    birthday = request.POST.get("birthday")
    description = request.POST.get("description")
    author = models.Author(name=name, sex=sex, birthday=birthday, description=description)
    obj = author.save()
    if(not obj):
        return HttpResponse('ok')


# 添加出版社
def publish_add(request):
    name = request.POST.get("name").strip(' ')
    addr = request.POST.get("addr")
    publish = models.Publish(name=name, addr=addr)
    obj = publish.save()
    # obj = models.Publish.objects.create(**data)
    if(not obj):
        return HttpResponse('ok')


# 添加读者信息
def reader_add(request):
    if request.method == 'GET':
        obj = models.Reader.objects.all()
        return render(request, 'menu_reader_add.html', locals())
    else:
        obj = {}
        obj["name"] = request.POST.get("name").strip(' ')
        obj["certificate"] = request.POST.get("certificate").strip(' ')
        obj["password"] = request.POST.get("password").strip(' ')
        obj["availableBooks"] = request.POST.get("availableBooks")
        reader = models.Reader(**obj)
        flag = reader.save()
        if(not flag):
            return redirect('/ul/menu/reader/')
        else:
            obj['error'] = flag
            return render(request, 'menu_reader_add.html', locals())


# 编辑书籍
def book_edit(request):
    if request.method == 'GET':
        book_id = request.GET.get('id')
        obj = models.Book.objects.filter(id=book_id).first()
        publishs = models.Publish.objects.all()
        authors = models.Author.objects.all()
        author_list = []
        for author in obj.author.all():
            author_list.append(author.id)
        return render(request, 'menu_book_edit.html', locals())
    else:
        book_id = request.GET.get('id')
        obj = request.POST.dict()
        for key in obj.keys():
            obj[key] = obj[key].strip(' ')
        print(obj)
        if ("author_id" in obj):
            obj.pop("author_id")
        book = models.Book.objects.filter(id=book_id).first()
        book.__dict__.update(**obj)
        book.author.clear()
        flag = book.save()
        author_id = request.POST.getlist('author_id')
        authors_list = models.Author.objects.filter(id__in=author_id)
        if len(author_id) != 0 and not flag:
            book.author.add(*authors_list)
            flag = book.save()
            return redirect('/ul/menu/book/')

        obj["author_error"] = "作者不能为空"
        author_list = []
        for author in authors_list:
            author_list.append(author.id)
        authors = models.Author.objects.all()
        publishs = models.Publish.objects.all()
        obj['error'] = flag
        obj["publish_id"] = int(obj["publish_id"])
        obj["publishDate"] = datetime.datetime.strptime(obj["publishDate"], '%Y-%m-%d')
        obj["enterDate"] = datetime.datetime.strptime(obj["enterDate"], '%Y-%m-%d')
        print(obj)
        return render(request, 'menu_book_edit.html', locals())


# 编辑作者信息
def author_edit(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        obj = models.Author.objects.get(id=id)
        list = ["男", "女", "保密"]
        # dict = {"男": "男", "女": "女", "保密": "保密"}
        return render(request, 'menu_author_edit.html', locals())
    else:
        id = request.GET.get('id')
        obj = request.POST.dict()
        for key in obj.keys():
            obj[key] = obj[key].strip(' ')
        author = models.Author.objects.filter(id=id).first()
        author.__dict__.update(**obj)
        flag = author.save()
        if (not flag):
            return redirect('/ul/menu/author/')
        else:
            obj["error"] = flag
            list = ["男", "女", "保密"]
            return render(request, 'menu_author_edit.html', locals())


# 编辑出版社信息
def publish_edit(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        obj = models.Publish.objects.get(id=id)
        return render(request, 'menu_publish_edit.html', locals())
    else:
        id = request.GET.get('id')
        obj = request.POST.dict()
        for key in obj.keys():
            obj[key] = obj[key].strip(' ')
        publish = models.Publish.objects.filter(id=id).first()
        publish.__dict__.update(**obj)
        flag = publish.save()
        if(not flag):
            return redirect('/ul/menu/publish/')
        else:
            obj["error"] = flag
            return render(request, 'menu_publish_edit.html', locals())


# 编辑读者信息
def reader_edit(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        obj = models.Reader.objects.get(id=id)
        return render(request, 'menu_reader_edit.html', locals())
    else:
        id = request.GET.get('id')
        obj = request.POST.dict()
        for key in obj.keys():
            obj[key] = obj[key].strip(' ')
        reader = models.Reader.objects.filter(id=id).first()

        reader.__dict__.update(**obj)
        flag = reader.save()
        if (not flag):
            return redirect('/ul/menu/reader/')
        else:
            obj["error"] = flag
            return render(request, 'menu_reader_edit.html', locals())


# 编辑借阅管理日志
def borrowingLog_edit(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        borrowingLog = models.BorrowingLog.objects.get(id=id)
        return render(request, 'menu_borrowingLog_edit.html', locals())
    else:
        dict = {}
        id = request.GET.get('id')
        data = request.POST.dict()
        print(data)
        for key in list(data.keys()):
            if not data[key].strip(' '):
                data.pop(key)
        borrowingLog = models.BorrowingLog.objects.filter(id=id).first()
        if data:
            borrowingLog.__dict__.update(**data)
        flag = borrowingLog.save()
        print(flag)
        if flag:
            dict["error"] = flag
            return render(request, 'menu_borrowingLog_edit.html', locals())
        else:
            return redirect('/ul/menu/borrowingLog/')


# 借书操作
def book_borrow(request):
    id = request.POST.get('id')
    certificate = request.POST.get("certificate").strip(' ')
    days = request.POST.get("days").strip(' ')
    # days = re.match('/^[0-9]+$/',days)
    str = ''
    try:
        days = int(days)
    except ValueError as e:
        str = '时长必须是一个整数'
        return HttpResponse(str)
    # print(days)

    if id and certificate and days:
        print('1')
        book = models.Book.objects.filter(id=id).first()
        reader = models.Reader.objects.filter(certificate=certificate).first()
        if book:
            totalCount = book.totalCount
            borrowCount = book.borrowCount
            if totalCount > borrowCount:
                if reader:
                    print('2')
                    availableBooks = reader.availableBooks
                    borrowedBooks = reader.borrowedBooks
                    if availableBooks > borrowedBooks:
                        borrowingLog = models.BorrowingLog.objects.create(book=book, reader=reader, days=days)
                        flag = isinstance(borrowingLog, models.BorrowingLog)
                        if flag:
                            print('3')
                            reader.__dict__.update(borrowedBooks=borrowedBooks+1)
                            reader.save()
                            book.__dict__.update(borrowCount=borrowCount+1)
                            book.save()
                            return HttpResponse('ok')
                    else:
                        str = '你的可借书籍数已达上限'
                else:
                    str = '读者证号有误'
            else:
                str = '该书暂无库存'
    else:
        str = '借书失败！！（注意读者证号的填写）'

    # print(totalCount)
    # str = 'ok'+certificate+';'+days+';'+id
    # print(str)
    return HttpResponse(str)


# 归还书籍操作
def borrowingLog_return(request):
    id = request.GET.get("id")
    borrowingLog = models.BorrowingLog.objects.filter(id=id).first()
    book = borrowingLog.book
    reader = borrowingLog.reader
    book.__dict__.update(borrowCount=book.borrowCount-1)
    reader.__dict__.update(borrowedBooks=reader.borrowedBooks-1)
    borrowingLog.__dict__.update(returned=True)
    flag = borrowingLog.save()
    if not flag:
        print(flag)
        book.save()
        reader.save()
        return redirect('/ul/menu/borrowingLog/')


# 删除书籍
def book_del(request):
    book_id = request.GET.get('id')
    models.Book.objects.filter(id=book_id).delete()
    return redirect('/ul/menu/book/')


# 删除作者信息
def author_del(request):
    id = request.GET.get("id")
    models.Author.objects.filter(id=id).delete()
    return redirect('/ul/menu/author/')


# 删除出版社信息
def publish_del(request):
    id = request.GET.get("id")
    models.Publish.objects.filter(id=id).delete()
    return redirect('/ul/menu/publish/')


# 删除借阅记录信息
def reader_del(request):
    id = request.GET.get("id")
    models.Reader.objects.filter(id=id).delete()
    return redirect('/ul/menu/reader/')


# 删除借阅记录信息
def borrowingLog_del(request):
    id = request.GET.get("id")
    models.BorrowingLog.objects.filter(id=id).delete()
    return redirect('/ul/menu/borrowingLog/')


# 查询书籍
TITLE = {}
def book_query(request):
    global TITLE
    title = ''
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            TITLE['book'] = title
        else:
            return redirect('/ul/menu/book/')
    else:
        title = TITLE.book
    page_number = request.GET.get("page")
    books1 = models.Book.objects.filter(title__icontains=title)
    # books = models.Book.objects.filter(publish_id__in=[title])
    books2 = models.Book.objects.filter(price__icontains=title)
    books = books1 | books2

    print(books)
    p = Paginator(books, 8)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'query.html', locals())


def book_detail(request):
    id = request.GET.get('id')
    obj = models.Book.objects.get(id=id)
    # authors = obj.author.all()
    # print(authors)
    return render(request, 'menu_book_detail.html', locals())
