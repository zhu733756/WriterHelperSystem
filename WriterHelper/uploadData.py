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

class UploadData(object):

    def __init__(self):
        self.author=None
        self.book=None
        self.category="小说"


    def get_bookpath(self,book_path):
        '''
        yield file paths of a book
        :param file_path:
        :return:
        '''
        self.author=os.path.split(book_path)[-1]
        for book in os.listdir(book_path):
            self.book=book
            yield os.path.join(book_path, self.book)

    def handle_titles_of_one_book(self,file_path):
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
        with open(file_path, "r", encoding="utf-8") as f:
            content = "".join(filter(lambda x: len(x) > 10, f.readlines()))
        arcticle_obj, _ = Arcticle.objects.get_or_create(
            title=os.path.split(file_path)[-1].split(".")[0],
            content=content, )
        arcticle_obj.bookname = book_obj
        arcticle_obj.authors.add(author_obj)
        arcticle_obj.categories.add(category_obj)
        arcticle_obj.save()

    def main(self):
        '''
        threadpools for handling books of an author
        :return:
        '''
        author_books_path=[]
        for author_path in os.listdir(NovelsPath):
            authors_path=os.path.join(NovelsPath,author_path)
            for book_path in os.listdir(authors_path):
                author_books_path.append(os.path.join(authors_path,book_path))
        total=len(author_books_path)
        with Pool(5) as pool:
            _=[x for x in tqdm(
                    pool.imap(func=self.handle_titles_of_one_book,iterable=author_books_path),
                    total=total)
               ]

if __name__ == '__main__':
    UploadData().main()