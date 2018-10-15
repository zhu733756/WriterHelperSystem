# -*- coding: utf-8 -*-
"""
@author: zh
"""
from MultiprocessAsyncSpider import load_biquge
from split_words import generate_key
from multiprocessing import Process,Manager,Queue,freeze_support,Pool
from redis import StrictRedis,ConnectionPool
from scrapy_redis import spiders
import time,sys,os
import subprocess

class RedisQueue(object):

    def __init__(self, redis_key):
       self.__db= StrictRedis(connection_pool=ConnectionPool(host="localhost",port=6379))
       self.__db.flushdb()
       self.key = redis_key

    def qsize(self):
        '''
        # 返回队列里面list内元素的数量
        :return:
        '''
        return self.__db.llen(self.key)

    def contains(self,req):
        lis=self.__db.lrange(self.key,0,-1)
        return  any(map(lambda x:req in str(x),lis))

    def put(self, item):
        self.__db.rpush(self.key, item)  # 添加新元素到队列最右方

    def get(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.__db.blpop(self.key, timeout=timeout)#tuple type
        return item

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__db.lpop(self.key)
        return item

class Crawler(object):

    def __init__(self,input_q,out_q):
        self.q = input_q
        self._seen=set()
        self.out_q=out_q

    def mudownload(self,ins):

        p1 = Process(name="CrawlProcess-1", target=ins.get_queue, args=())
        p2 = Process(name="CrawlProcess-2", target=ins.get_queue, args=())
        p3 = Process(name="ProgressBarProcess", target=ins.ShellProgress, args=())
        for p in (p1, p2, p3):
            p.start()
        for p in (p1, p2, p3):
            p.join()
        if not p3.is_alive():
            p1.terminate()
            p2.terminate()

    def download(self,req):
        ins=load_biquge(req)
        ins.put_page_urls()
        print("url(%s)-total:"%req,ins.total)
        self.out_q.put(req+"@"+str(ins.total))
        # self.mudownload(ins)
        time.sleep(40)
        self.out_q.put(req + "@finished")

    def filter(self, items):
        for item in items:
            if item not in self._seen:
                yield item
                self._seen.add(item)

    def next_requests(self):
        while self.q.qsize():
            req = self.q.get_nowait()
            if not req:
                break
            req = req.decode() if isinstance(req, bytes) else req
            yield req

    def crawl(self):
        print("Waiting for req...")
        while 1:
            reqs=[req for req  in self.next_requests()]
            if reqs:
                for req in reqs:
                    print("Read a req({})".format(req))
                    self.download(req)
                else:
                    print("Etracted all,waiting for req...")
            time.sleep(1)

input_q=RedisQueue("Novels:enQueue")
out_q=RedisQueue("JS:outQueue")
crawler=Crawler(input_q,out_q)#Singleton

def crawler_push(items):
    items = list(crawler.filter(items))
    for item in items:
        print("put in queue:", item)
        crawler.q.put(item)
    else:
        print("Current Queue size:", crawler.q.qsize())
    return items

def check_enqueue(req):
    return crawler.q.contains(req)

def check_outqueue(req):
    return crawler.out_q.contains(req)

def getOutQueueEle():
    if not crawler.out_q.qsize():
        return None
    req= crawler.out_q.get_nowait()
    req = req.decode() if isinstance(req, bytes) else req
    return req

if "__main__"==__name__:

    crawler.crawl()






