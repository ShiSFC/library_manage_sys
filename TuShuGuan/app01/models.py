from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator, MinLengthValidator, RegexValidator
from django.db import models, IntegrityError
from django import forms
import datetime
from django.utils import timezone


class SaveModel(models.Model):
    # 抽象类
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        error = {}
        try:
            self.full_clean()  # 验证
            super().save(*args, **kwargs)
        except ValidationError as e:
            print('模型验证没通过： %s' % e.message_dict)
            error = e.message_dict
        if error:
            return error


class Author(SaveModel):
    SEX_IN_CHOICE = [
        ("男", "男"),
        ("女", "女"),
        ("保密", "保密")
    ]
    name = models.CharField(max_length=32)
    sex = models.CharField(max_length=7, choices=SEX_IN_CHOICE, default="保密")
    # age = models.IntegerField()  # 可不要
    birthday = models.DateField(null=True, blank=True)
    # university = models.CharField(max_length=32)
    description = models.TextField(null=True, blank=True)


class Publish(SaveModel):
    name = models.CharField(max_length=32, validators=[MinLengthValidator(1)])
    addr = models.CharField(max_length=32, null=True, blank=True)


class Book(SaveModel):
    title = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    publishDate = models.DateField()
    totalCount = models.PositiveIntegerField(default=0)
    borrowCount = models.PositiveIntegerField(default=0)
    # isShow = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    isbn = models.CharField(max_length=13, validators=[RegexValidator(r'^97[89][0-9]{10}$', "请填写正确的ISBN")])
    classification = models.CharField(max_length=32)  # 分类号
    enterDate = models.DateField()  # default=datetime.date.today() # 入库时间
    publish = models.ForeignKey('Publish', on_delete=models.PROTECT)
    author = models.ManyToManyField('Author')


def getNo():
    NO = "0000000001"
    def addOne(num):
        nonlocal NO
        no = str(int(NO) + int(num))
        NO = "0" * (10 - len(no)) + no
        return NO
    return addOne
ADDONE = getNo()


class Reader(models.Model):
    certificate = models.CharField(unique=True, max_length=10, validators=[RegexValidator(r'^[0-9]{10}$', "借书证号只能为10位数字")])
    name = models.CharField(max_length=16, null=True, blank=True)
    password = models.CharField(max_length=16)
    availableBooks = models.IntegerField(default=4)
    borrowedBooks = models.IntegerField(default=0)

    class Meta:
        db_table = 'app01_reader'
        ordering = ('certificate',)

    def save(self, *args, **kwargs):
        error = {}
        try:
            # 自动给出读者证号，从1开始
            if not self.certificate:
                self.certificate = ADDONE(1)
                while self.cus_validate_unique():
                    self.certificate = ADDONE(1)
            self.full_clean()
            super().save(*args, **kwargs)
        except ValidationError as e:
            print('reader模型验证没通过： %s' % e.message_dict)
            error = e.message_dict
        if error:
            if not self.certificate:
                ADDONE(-1)
            # print(self.certificate)
            return error

    def cus_validate_unique(self):
        error = {}
        try:
            self.validate_unique()
        except ValidationError as e:
            print('reader模型唯一性验证没通过： %s' % e.message_dict)
            error = e.message_dict
        if error:
            return error


class BorrowingLog(SaveModel):
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    reader = models.ForeignKey(Reader, on_delete=models.PROTECT)
    borrow = models.BooleanField(default=True)
    returned = models.BooleanField(default=False)
    borrowDate = models.DateTimeField(default=timezone.now)  # auto_now_add=True 或者 default=timezone.now  django.utils.timezone.now()
    returnedDate = models.DateTimeField(null=True, blank=True)   # DateField default=datetime.date.today()
    days = models.PositiveIntegerField(default=60)
    actualDate = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            self.returnedDate = self.borrowDate + datetime.timedelta(days=self.days)
            if self.returned:
                self.actualDate = timezone.now()
            error = super().save(*args, **kwargs)
        except ValidationError as e:
            print('模型验证没通过： %s' % e.message_dict)
            error = e.message_dict
        if error:
            return error

    class Meta:
        db_table = 'app01_borrowingLog'
        ordering = ('returned', '-actualDate',)


class Regist(forms.Form):
    username = forms.CharField(
        error_messages={'required': '用户名错误'},
        min_length=4,
        widget=forms.TextInput(
            attrs={'class': "form-control", 'placeholder': '用户名'}
        )
    )
    password = forms.CharField(
        error_messages={'required': '密码不能为空'},
        min_length=6,
        widget=forms.PasswordInput(
            attrs={'class': "form-control", 'placeholder': '密码'}
        )
    )
    email = forms.EmailField(
        error_messages={'required': '邮箱不能为空'},
        widget=forms.EmailInput(
            attrs={'class': "form-control", 'placeholder': '邮箱'}
        )
    )


class Log_in(forms.Form):
    user = forms.CharField(
        error_messages={'required': '用户名不能为空'},
        widget=forms.TextInput(
            attrs={'class': "form-control", 'placeholder': '用户名'})
    )
    pwd = forms.CharField(
        min_length=6,
        error_messages={'required': '密码不能为空'},
        widget=forms.PasswordInput(
            attrs={'class': "form-control", 'placeholder': '密码'})
    )
