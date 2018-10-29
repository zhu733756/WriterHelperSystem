from django.db import models
from tinymce.models import HTMLField

class Author(models.Model):
    name = models.CharField("作者",max_length=50)

    def __str__(self):
        return self.name

class Category(models.Model):
    category = models.CharField("文章分类", max_length=100)  # 分类

    def __str__(self):
        return self.category

class Book(models.Model):
    name=models.CharField("书籍名称",max_length=50)

    def __str__(self):
        return self.name

class Arcticle(models.Model):

    title = models.CharField('标题', max_length=128)
    content = HTMLField("内容")

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author)
    categories = models.ManyToManyField(Category)

    pub_time = models.DateTimeField('发表时间', auto_now_add=True, editable=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True)

    def __str__(self):
        return self.title
