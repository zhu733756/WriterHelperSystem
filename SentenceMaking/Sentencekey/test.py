# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""

import os,json

with open("D:\gitdata\gitdataRes\WriterHelperSystem\SentenceMaking\Sentencekey\失落叶-斩龙\idiom.json","r",encoding="utf8") as f:
    for n,file in enumerate(f.readlines()):
        try:
            s=json.loads(file).values()
            print(s)
        except:
            print(n)

