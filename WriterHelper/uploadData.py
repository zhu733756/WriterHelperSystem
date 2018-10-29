# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""
import os,django,datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WriterHelper.settings")
django.setup()

from Novel.models import Author,Book,Category,Arcticle

BasePath=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NovelsPath=os.path.join(BasePath,"SentenceMaking/NovelsRawData/失落叶/天行")

def main():

    author=os.path.split(os.path.dirname(NovelsPath))[-1]
    bookname =os.path.split(NovelsPath)[-1]
    author_obj,_ = Author.objects.get_or_create(name=author)
    book_obj,_ = Book.objects.get_or_create(name=bookname)
    category_obj,_ = Category.objects.get_or_create(category="小说")
    print(category_obj,author_obj,book_obj)
    title=os.listdir(NovelsPath)[0]
    with open(os.path.join(NovelsPath,title),"r",encoding="utf-8") as f:
        content=f.read()
    arcticle_obj,_= Arcticle.objects.get_or_create(
            title=title.split(".")[0],
            content=content,
            book=book_obj
        )
    arcticle_obj.authors.add(author_obj)
    arcticle_obj.categories.add(category_obj)
    print(arcticle_obj)
    print("---------")

if __name__ == '__main__':
    main()
    print("finished!")