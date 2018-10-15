# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""
#
# class A(object):
#     _instance=None
#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance=super(A,cls).__new__(cls)
#         return cls._instance
#
# class Singleton(type):
#     _instance={}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instance:
#             cls._instance[cls]=super(Singleton,cls).__call__(*args,**kwargs)
#         return cls._instance[cls]
#
# class Myclass(A):
#     def __init__(self, m):
#         self.m = m
#
# class myclass(metaclass=Singleton):
#    def __init__(self,m):
#        self.m=m
#
#
# c=1
# d=2
# subclass=Myclass(m=1)
# subclass2=Myclass(m=2)
# print(subclass.m)
# print(subclass2.m)
#
# from functools import wraps
# def singleton2(cls):
#     instances={}
#     @wraps(cls)
#     def getinstance(*args,**kw):
#         if cls not in instances:
#             instances[cls]=cls(*args,**kw)
#         return instances[cls]
#     return getinstance
#
# @singleton2
# class B(object):
#     def __init__(self,m):
#         self.m=m
#
# a=B(m=1)
# b=B(m=2)
# print(a.m)
# print(b.m)

# import tqdm,time,random
#
# pbar = tqdm.tqdm(total=80)
# while True:
#     tmp=random.choice([7,8,9])
#     if tmp >pbar.total:
#         pbar.update(pbar.total-pbar.n)
#         break
#     pbar.update(tmp)
#     time.sleep(1)
# pbar.close()

# from collections import deque
#
# l=deque([1,2,4,6],maxlen=4)
# l.append(0)
# print(l)
# print(l.pop())
#
# s={"a":1,"b":2}
# s2={}
# s2.update(s)
# print(s2)
#
# valid_urls=[1,2,4]
# res={url:"ok" for url in valid_urls}
# print(res)
#
# a={}
#
# def get():
#     global a
#     print(a)
#     a.update({"a":0})
#     print(a)
#
# get()
# print(a)
#
#
# class ABC(object):
#
#     def __init__(self,a):
#         self.a=a
#
#     def get_a(self,m):
#         return m
# print("====")
# print(ABC)
# print(ABC(1).__getattribute__("get_a")(2))
# print(ABC(1))
# print("----")
#
# print({b"https://www.biquge5200.cc/7_7222/":123})
#
# urls=["https://www.biquge5200.cc/7_7222/"]
# res={url:"success" for url in urls}
# print(res)
#
# import re
# title="*.?? wo"
# title = re.compile(r"[*.?？\s<>]+").sub("", title)
# print(title)
#
# print(bytes("https://www.biquge5200.cc/7_7222/",encoding="utf-8").decode())
# print(isinstance(b'',bytes))
#
# print("https://www.biquge5200.cc/62_62835/".split("/")[-2])

def printF(num):
    print("num:",num)
    return "123"

# printF(124)
#
# print(0%100)
lis=[b"123",b"1",b"2"]
req="1"
print(list(filter(lambda x:req in str(x),lis)))

