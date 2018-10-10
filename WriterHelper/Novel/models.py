from django.db import models
from tinymce.models import HTMLField


class Arcticle(models.Model):
    name = models.CharField("文章分类",max_length=100)#分类
    tagline = models.TextField("标签",max_length=100)#标签

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField("作者",max_length=50)

    def __str__(self):
        return self.name

class Novel(models.Model):
    arcticles=models.ForeignKey(Arcticle, on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author)
    novel_name = models.CharField("小说名", max_length=128)
    title = models.CharField('标题', max_length=128)
    content = HTMLField("内容")
    pub_date = models.DateTimeField('发表时间', auto_now_add=True, editable=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True)

    def __str__(self):
        return self.title
