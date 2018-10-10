# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""
import  os

path=os.path.dirname(os.path.dirname(__file__))

SentenceKeyPath=os.path.join(path,"SentenceKey")

for dirpath in os.listdir(SentenceKeyPath):
    if os.path.isdir(os.path.join(SentenceKeyPath,dirpath)):
        with open("./author_novel.txt","w+",encoding="utf-8") as f:
            f.write(dirpath+"\n")
else:
    print("done!")