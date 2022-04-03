import datetime
import re

from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.db.models import ProtectedError
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
    p = Paginator(books, 10)
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
    return render(request, 'menu_author.html', locals())


# 出版社信息
def publish(request):
    page_number = request.GET.get("page")
    book_lists = models.Publish.objects.all()
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
    return render(request, 'menu_publish.html', locals())


# 读者信息
def reader(request):
    page_number = request.GET.get("page")
    readers = models.Reader.objects.all() #.order_by('certificate')
    p = Paginator(readers, 10)
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
    # print(request.get_full_path())
    page_number = request.GET.get("page")
    returned = request.GET.get("return")
    book_lists = models.BorrowingLog.objects.all()
    if returned == 'f':
        book_lists = models.BorrowingLog.objects.filter(returned=False)
    elif returned == 't':
        book_lists = models.BorrowingLog.objects.filter(returned=True)
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
    url = request.get_full_path()
    # print(url)
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
    try:
        book_id = request.GET.get('id')
        models.Book.objects.filter(id=book_id).delete()
        return redirect('/ul/menu/book/')
    except IntegrityError:
        return HttpResponse('不可删除')


# 删除作者信息
def author_del(request):
    try:
        id = request.GET.get("id")
        models.Author.objects.filter(id=id).delete()
        return redirect('/ul/menu/author/')
    except IntegrityError:
        return HttpResponse('不可删除')


# 删除出版社信息
def publish_del(request):
    try:
        id = request.GET.get("id")
        models.Publish.objects.filter(id=id).delete()
        return redirect('/ul/menu/publish/')
    except IntegrityError:
        return HttpResponse('不可删除')


# 删除读者信息
def reader_del(request):
    try:
        id = request.GET.get("id")
        models.Reader.objects.filter(id=id).delete()
        return redirect('/ul/menu/reader/')
    except IntegrityError:
        return HttpResponse('不可删除')


# 删除借阅记录信息
def borrowingLog_del(request):
    try:
        id = request.GET.get("id")
        models.BorrowingLog.objects.filter(id=id).delete()
        return redirect('/ul/menu/borrowingLog/')
    except IntegrityError:
        return HttpResponse('不可删除')


# 书籍详情
def book_detail(request):
    id = request.GET.get('id')
    obj = models.Book.objects.filter(id=id).first()
    if obj:
        logs = obj.borrowinglog_set.filter(returned=False)
        # authors = obj.author.all()
        # print(authors)
        return render(request, 'menu_book_detail.html', locals())
    # except ValueError as e:
    else:
        return HttpResponse('该书籍不存在！')


TITLE = {}
# 查询书籍
def book_query(request):
    global TITLE
    title = ''
    if request.method == 'POST':
        title = request.POST.get('title').strip(' ')
        if title:
            TITLE['book'] = title
        else:
            return redirect('book_show')
    else:
        title = TITLE['book']
    page_number = request.GET.get("page")
    books = models.Book.objects.filter(title__icontains=title)
    # 多对一查询
    publishs = models.Publish.objects.filter(name__icontains=title)
    for publish in publishs:
        books2 = publish.book_set.all()
        books = books | books2
    # 多对多查询
    authors = models.Author.objects.filter(name__icontains=title)
    for author in authors:
        books3 = author.book_set.all()
        books = books | books3
    # 去重
    books = books.distinct()
    # books = list(set(books))
    # print(books)
    p = Paginator(books, 10)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_book_query.html', locals())


# 查询作者
def author_query(request):
    global TITLE
    title = ''
    if request.method == 'POST':
        title = request.POST.get('author').strip(' ')
        if title:
            TITLE['author'] = title
        else:
            return redirect('author_show')
    else:
        print(TITLE)
        title = TITLE['author']
    page_number = request.GET.get("page")
    authors = models.Author.objects.filter(name__icontains=title)
    print(authors)
    p = Paginator(authors, 10)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_author_query.html', locals())


# 查询出版社
def publish_query(request):
    global TITLE
    title = ''
    if request.method == 'POST':
        title = request.POST.get('publish').strip(' ')
        if title:
            TITLE['publish'] = title
        else:
            return redirect('publish_show')
    else:
        title = TITLE['publish']
    page_number = request.GET.get("page")
    publishs = models.Publish.objects.filter(name__icontains=title)
    p = Paginator(publishs, 10)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_publish_query.html', locals())


# 查询读者
def reader_query(request):
    global TITLE
    title = ''
    if request.method == 'POST':
        title = request.POST.get('reader').strip(' ')
        if title:
            TITLE['reader'] = title
        else:
            return redirect('reader_show')
    else:
        title = TITLE['reader']
    page_number = request.GET.get("page")
    readers = models.Reader.objects.filter(name__icontains=title)
    if re.match('^[0-9]{10}$', title):
        reader = models.Reader.objects.filter(certificate=title)
        readers = readers | reader
    readers = list(set(readers))
    # print(readers)
    p = Paginator(readers, 10)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_reader_query.html', locals())


# 查询借阅信息
def borrowingLog_query(request):
    global TITLE
    title = ''
    if request.method == 'POST':
        title = request.POST.get('borrowingLog')
        if title:
            TITLE['borrowingLog'] = title
        else:
            return redirect('borrowingLog_query')
    else:
        title = TITLE['borrowingLog']
    page_number = request.GET.get("page")
    borrowing_logs = models.BorrowingLog.objects.filter()
    print(borrowing_logs)
    borrowing_logs = borrowing_logs.none()
    print(borrowing_logs)

    # 借阅者搜素
    readers = models.Reader.objects.filter(name__icontains=title)
    if re.match('^[0-9]{10}$', title):
        reader = models.Reader.objects.filter(certificate=title)
        readers = readers | reader
    for reader in readers:
        log = reader.borrowinglog_set.all()
        borrowing_logs = borrowing_logs | log

    # 书籍搜索
    books = models.Book.objects.filter(title__icontains=title)
    for book in books:
        log = book.borrowinglog_set.all()
        borrowing_logs = borrowing_logs | log

    # borrowing_logs.distinct().order_by('name')
    # borrowing_logs = list(set(borrowing_logs))
    print(borrowing_logs)
    p = Paginator(borrowing_logs, 10)
    try:
        book_list = p.page(page_number)
        page_number = int(page_number)
    except EmptyPage:
        book_list = p.page(p.num_pages)
        page_number = p.num_pages
    except PageNotAnInteger:
        book_list = p.page(1)
        page_number = 1
    return render(request, 'menu_borrowingLog_query.html', locals())


# 查询借阅信息
def borrowingLog_query_not_return(request):
    # global TITLE
    # title = ''
    # if request.method == 'POST':
    #     title = request.POST.get('borrowingLog')
    #     if title:
    #         TITLE['borrowingLog'] = title
    #     else:
    #         return redirect('borrowingLog_query')
    # else:
    #     title = TITLE['borrowingLog']
    page_number = request.GET.get("page")
    borrowing_logs = models.BorrowingLog.objects.filter(returned=False)
    print(borrowing_logs)
    # borrowing_logs = borrowing_logs.none()
    # print(borrowing_logs)
    p = Paginator(borrowing_logs, 10)
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
