# -*- coding: utf-8 -*-
"""
@author: zh
"""
from MultiprocessAsyncSpider import load_biquge
from split_words import generate_key
from multiprocessing import Process,Manager,Queue,freeze_support
from redis import StrictRedis,ConnectionPool
from scrapy_redis import spiders
import time

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

    def download(self,req):
        ins=load_biquge(req)
        ins.put_page_urls()
        print("url(%s)-total:"%req,ins.total)
        self.out_q.put(req+"@"+str(ins.total))
        p1 = Process(name="CrawlProcess-1", target=ins.get_queue, args=())
        p2 = Process(name="CrawlProcess-2", target=ins.get_queue, args=())
        p3 = Process(name="ProgressBarProcess", target=ins.ShellProgress, args=())
        for p in (p1, p2, p3):
            p.start()
        for p in (p1, p2, p3):
            p.join()
        self.out_q.put(req + "@finished")

    def filter(self, items):
        for item in items:
            if item not in self._seen:
                yield item
                self._seen.add(item)

    def push(self, items):
        for item in items:
            print("put in queue:",item)
            self.q.put(item)
        else:
            print(self.q.qsize())

    def next_requests(self):
        found=0
        while found < self.q.qsize():
            req = self.q.get_nowait()
            if not req:
                break
            yield req
            found += 1

    def crawl(self):
        while 1:
            print("Wait for req...")
            for req in self.next_requests():
                print("Read a req({})".format(req))
                self.download(req)
            time.sleep(0.5)

input_q=Queue()
out_q=Queue()
crawler=Crawler(input_q,out_q)#Singleton

def crawler_push(items):
    items = list(crawler.filter(items))
    crawler.push(items)
    print(crawler.q.qsize())
    return items

def getOutQueueEle():
    if not crawler.out_q.qsize():
        return None
    req= crawler.out_q.get_nowait()
    req = req.decode() if isinstance(req, bytes) else req
    return req

if "__main__"==__name__:

    items=["https://www.biquge5200.cc/0_46/","https://www.biquge5200.cc/7_7222/"]
    crawler_push(items)
    crawler.crawl()






