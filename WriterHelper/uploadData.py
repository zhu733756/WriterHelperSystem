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
    for title in os.listdir(NovelsPath)[:100]:
        testFilesPath = os.path.join(NovelsPath, title)
        with open(testFilesPath,"r",encoding="utf-8") as f:
            content=f.read()
        Arcticle.objects.get_or_create(
                authors=author,
                book_name=bookname,
                title=title,
                category="小说",
                content=content,
            )

if __name__ == '__main__':
    main()
    print("finished!")