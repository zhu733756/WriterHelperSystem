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
from multiprocessing.dummy import Pool
from tqdm import tqdm

BasePath=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NovelsPath=os.path.join(BasePath,"SentenceMaking/NovelsRawData/")
authors_path = [os.path.join(NovelsPath,author) for author in os.listdir(NovelsPath)]

class UploadData(object):

    def __init__(self):
        self.author=None
        self.book=None
        self.title=None
        self.category="小说"

    def get_bookpath(self,author_path):
        '''
        yield paths of a book
        :param author_path:
        :return:
        '''
        self.author=os.path.split(author_path)[-1]
        for book in os.listdir(author_path):
            self.book=book
            book_path = os.path.join(author_path, self.book)
            yield book_path

    def handle_titles_of_one_book(self,book_path):
        '''
        a progressbar during handling arcticles of a book
        :param book_path:
        :return:
        '''
        author_obj,_ = Author.objects.get_or_create(name=self.author)
        book_obj,_ = Book.objects.get_or_create(name=self.book)
        category_obj,_ = Category.objects.get_or_create(category=self.category)
        author_obj.save()
        book_obj.save()
        category_obj.save()
        for title in tqdm(
                os.listdir(book_path),
                desc="Upload Data(%s|%s)"%(self.author,self.book)):
            with open(os.path.join(book_path,title),"r",encoding="utf-8") as f:
                content="".join(filter(lambda x:len(x)>10,f.readlines()))
            arcticle_obj,_=Arcticle.objects.get_or_create(
                    title=title.split(".")[0],
                    content=content,)
            arcticle_obj.bookname=book_obj
            arcticle_obj.authors.add(author_obj)
            arcticle_obj.categories.add(category_obj)
            arcticle_obj.save()

    def main(self):
        '''
        threadpools for handling books of an author
        :return:
        '''
        for author_path in authors_path:
            iterable=self.get_bookpath(author_path)
            with Pool(5) as pool:
                pool.map(func=self.handle_titles_of_one_book,iterable=iterable)

if __name__ == '__main__':
    UploadData().main()