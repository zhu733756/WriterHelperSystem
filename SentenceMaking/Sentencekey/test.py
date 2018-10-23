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

with open("D:\gitdata\gitdataRes\WriterHelperSystem\SentenceMaking\Sentencekey\辰东-完美世界\idiom.json","r",encoding="utf8") as f:
    lines=filter(lambda x: x.strip(),f.read().split("\n"))
    for n,file in enumerate(lines):
        try:
            s=json.loads(file).keys()
            print(s)
        except:
            print(n)

